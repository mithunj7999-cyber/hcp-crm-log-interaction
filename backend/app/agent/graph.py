"""
HCP CRM — LangGraph Agent Graph.

Builds a ReAct-style agent using LangGraph that routes user messages
through Groq LLM (gemma2-9b-it primary, llama-3.3-70b-versatile fallback)
and can invoke the 5 HCP tools.
"""

import json
import logging
from typing import Annotated, TypedDict, Sequence

from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage,
)
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.core.config import get_settings
from app.agent.tools import ALL_TOOLS

logger = logging.getLogger(__name__)
settings = get_settings()

# ── System prompt ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system used by field representatives to log interactions with Healthcare Professionals (HCPs).

Your primary responsibilities:
1. **Log Interactions**: When a user describes a meeting/call/email with an HCP, extract all relevant details and use the `log_interaction` tool to save it. Extract: HCP name, interaction type, topics discussed, materials shared, samples distributed, sentiment (Positive/Neutral/Negative), outcomes, and follow-up actions.

2. **Edit Interactions**: When asked to modify a previously logged interaction, use the `edit_interaction` tool with the interaction ID, field name, and new value.

3. **Suggest Follow-ups**: After logging an interaction, proactively use `suggest_followups` to generate 2-3 actionable next steps. Present these as short, specific suggestions.

4. **Search HCP History**: When the user mentions an HCP or wants context, use `search_hcp_history` to retrieve their profile and past interactions.

5. **Look Up Materials**: When topics are discussed, use `materials_lookup` to find relevant brochures, clinical data, samples, or presentations that could be shared.

IMPORTANT RULES:
- Always try to extract as much information as possible from the user's message.
- If the HCP name is mentioned, always use it to search the database; if it does not exist yet, create a new HCP record automatically.
- For sentiment, infer from context clues: words like "interested", "excited", "agreed" → Positive; "hesitant", "declined", "concerned" → Negative; otherwise → Neutral.
- After logging, always call `suggest_followups` with the new interaction ID.
- Present follow-up suggestions as a numbered list.
- Be concise but thorough in your responses.
- When confirming a logged interaction, list all the fields that were populated.
- Today's date is used automatically if no date is mentioned.
"""


# ── Agent State ─────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """State passed between graph nodes."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ── Build the LLM (with fallback) ──────────────────────────────────────

def _build_llm() -> ChatGroq:
    """Create the primary Groq LLM with tool-binding."""
    primary = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL,
        temperature=0.3,
        max_tokens=2048,
    )
    return primary


def _build_fallback_llm() -> ChatGroq:
    """Create the fallback Groq LLM."""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_FALLBACK_MODEL,
        temperature=0.3,
        max_tokens=2048,
    )


# ── Graph nodes ─────────────────────────────────────────────────────────

def agent_node(state: AgentState) -> dict:
    """Call the LLM with the current message history + bound tools."""
    messages = list(state["messages"])

    # Ensure system prompt is present
    if not messages or not isinstance(messages[0], SystemMessage):
        messages.insert(0, SystemMessage(content=SYSTEM_PROMPT))

    # Try primary model, fall back if it fails
    try:
        llm = _build_llm().bind_tools(ALL_TOOLS)
        response = llm.invoke(messages)
    except Exception as e:
        logger.warning(f"Primary model ({settings.GROQ_MODEL}) failed: {e}. Falling back to {settings.GROQ_FALLBACK_MODEL}.")
        try:
            llm = _build_fallback_llm().bind_tools(ALL_TOOLS)
            response = llm.invoke(messages)
        except Exception as fallback_err:
            logger.error(f"Fallback model also failed: {fallback_err}")
            response = AIMessage(
                content="I'm sorry, I'm having trouble processing your request right now. "
                        "Please try again in a moment."
            )

    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Decide whether to call tools or end the conversation turn."""
    last_message = state["messages"][-1]

    # If the LLM returned tool calls, route to the tool node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "end"


# ── Build the graph ─────────────────────────────────────────────────────

def build_agent_graph() -> StateGraph:
    """Construct and compile the LangGraph agent."""

    tool_node = ToolNode(ALL_TOOLS)

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    # Set entry point
    graph.set_entry_point("agent")

    # Conditional edge: agent → tools or end
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        },
    )

    # After tools execute, go back to agent to process results
    graph.add_edge("tools", "agent")

    return graph.compile()


# ── Singleton compiled graph ────────────────────────────────────────────

_compiled_graph = None


def get_agent():
    """Return the compiled agent graph (lazy singleton)."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_agent_graph()
    return _compiled_graph


# ── Run the agent ───────────────────────────────────────────────────────

def run_agent(user_message: str, chat_history: list[dict] | None = None) -> dict:
    """
    Run the agent with a user message and optional chat history.

    Args:
        user_message: The user's natural-language input.
        chat_history: Optional list of prior messages [{"role": "user"|"assistant", "content": "..."}].

    Returns:
        dict with keys: reply (str), extracted_data (dict|None), suggestions (list|None)
    """
    agent = get_agent()

    # Build message history
    messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]

    if chat_history:
        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_message))

    # Invoke the graph
    result = agent.invoke({"messages": messages})

    # Extract the final response and any tool results
    final_messages = result["messages"]

    # Get the last AI message (the final reply)
    reply = ""
    extracted_data = None
    suggestions = None

    for msg in reversed(final_messages):
        if isinstance(msg, AIMessage) and msg.content:
            reply = msg.content
            break

    # Scan tool messages for extracted data and suggestions
    for msg in final_messages:
        if isinstance(msg, ToolMessage):
            try:
                tool_result = json.loads(msg.content)
                if tool_result.get("success"):
                    # Check if this is a log_interaction result (has hcp_id + id)
                    if "hcp_id" in tool_result and "id" in tool_result and "message" in tool_result:
                        extracted_data = {
                            k: v for k, v in tool_result.items()
                            if k not in ("success", "message", "instruction")
                        }
                    # Check if this is a suggest_followups result
                    if "instruction" in tool_result:
                        # The suggestions will be in the AI's response text
                        pass
            except (json.JSONDecodeError, TypeError):
                pass

    # Try to extract suggestions from the reply text
    if reply:
        suggestion_lines = []
        for line in reply.split("\n"):
            line = line.strip()
            if line and (
                line.startswith(("1.", "2.", "3.", "- ", "• "))
                or line.startswith(("1)", "2)", "3)"))
            ):
                # Clean up the suggestion text
                clean = line.lstrip("0123456789.)- •").strip()
                if clean and len(clean) > 5:
                    suggestion_lines.append(clean)
        if suggestion_lines:
            suggestions = suggestion_lines[:5]  # Cap at 5 suggestions

    return {
        "reply": reply,
        "extracted_data": extracted_data,
        "suggestions": suggestions,
    }
