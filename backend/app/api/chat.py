"""
HCP CRM — Chat API route (LangGraph agent endpoint).

POST /api/chat — sends user message to the AI agent
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI Chat"])


# ── Request / Response schemas ──────────────────────────────────────────

class ChatHistoryItem(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    """Incoming chat message from the AI assistant panel."""
    message: str = Field(..., min_length=1, description="Natural-language summary of the interaction")
    history: Optional[List[ChatHistoryItem]] = Field(
        default=None,
        description="Optional conversation history for context",
    )


class ChatResponse(BaseModel):
    """Response from the AI agent."""
    reply: str = Field(..., description="Agent's natural-language response")
    extracted_data: Optional[dict] = Field(
        default=None,
        description="Structured data extracted from the message (used to auto-fill the form)",
    )
    suggestions: Optional[List[str]] = Field(
        default=None,
        description="AI-suggested follow-up actions",
    )


# ── Route ───────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the AI agent.

    The agent will:
    - Parse the user's natural-language input
    - Invoke tools (log_interaction, edit_interaction, etc.) as needed
    - Return a reply + any extracted structured data + follow-up suggestions
    """
    try:
        from app.agent.graph import run_agent

        # Convert history to list of dicts
        history = None
        if request.history:
            history = [{"role": h.role, "content": h.content} for h in request.history]

        result = run_agent(
            user_message=request.message,
            chat_history=history,
        )

        return ChatResponse(
            reply=result["reply"],
            extracted_data=result.get("extracted_data"),
            suggestions=result.get("suggestions"),
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing failed: {str(e)}",
        )
