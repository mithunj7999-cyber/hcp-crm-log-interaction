"""
HCP CRM — LangGraph Agent Tools.

Five tools the agent can invoke:
  1. log_interaction       — Parse free-text → create interaction record
  2. edit_interaction      — Natural-language edit to an existing record
  3. suggest_followups     — Generate follow-up action suggestions
  4. search_hcp_history    — Retrieve past interactions for an HCP
  5. materials_lookup      — Find relevant materials by topic
"""

import json
from datetime import date, time, datetime
from typing import Optional

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.models import HCP, Interaction, Material, InteractionType, Sentiment


# ── Helper: get a fresh DB session ──────────────────────────────────────

def _get_db() -> Session:
    """Create and return a new DB session (caller must close)."""
    return SessionLocal()


def _serialize_interaction(interaction: Interaction) -> dict:
    """Convert an Interaction ORM object to a JSON-serializable dict."""
    return {
        "id": interaction.id,
        "hcp_id": interaction.hcp_id,
        "hcp_name": interaction.hcp.name if interaction.hcp else None,
        "interaction_type": interaction.interaction_type.value if interaction.interaction_type else None,
        "date": interaction.date.isoformat() if interaction.date else None,
        "time": interaction.time.isoformat() if interaction.time else None,
        "attendees": interaction.attendees,
        "topics_discussed": interaction.topics_discussed,
        "materials_shared": interaction.materials_shared,
        "samples_distributed": interaction.samples_distributed,
        "sentiment": interaction.sentiment.value if interaction.sentiment else None,
        "outcomes": interaction.outcomes,
        "follow_up_actions": interaction.follow_up_actions,
    }


# ═══════════════════════════════════════════════════════════════════════
# TOOL 1 — log_interaction
# ═══════════════════════════════════════════════════════════════════════

@tool
def log_interaction(
    hcp_name: str,
    interaction_type: str = "Meeting",
    topics_discussed: str = "",
    materials_shared: str = "",
    samples_distributed: str = "",
    sentiment: str = "Neutral",
    outcomes: str = "",
    follow_up_actions: str = "",
    attendees: str = "",
    date_str: str = "",
    time_str: str = "",
) -> str:
    """Log a new HCP interaction to the database.

    Use this tool after extracting structured fields from the user's
    free-text message. All fields are strings.

    Args:
        hcp_name: Full name of the Healthcare Professional (e.g. "Dr. Sarah Chen").
        interaction_type: One of Meeting, Call, Email, Video Call, Conference, Other.
        topics_discussed: Comma-separated topics discussed during the interaction.
        materials_shared: Comma-separated names of materials shared.
        samples_distributed: Comma-separated names of samples distributed.
        sentiment: One of Positive, Neutral, Negative — the observed HCP sentiment.
        outcomes: Summary of outcomes from the interaction.
        follow_up_actions: Planned follow-up actions.
        attendees: Comma-separated list of attendees.
        date_str: Date of interaction in YYYY-MM-DD format. Leave empty for today.
        time_str: Time of interaction in HH:MM format. Leave empty if not specified.
    """
    db = _get_db()
    try:
        # Resolve HCP by name (fuzzy match)
        hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name}%")).first()
        if not hcp:
            return json.dumps({
                "error": f"HCP '{hcp_name}' not found in the database. Please check the name and try again.",
                "success": False,
            })

        # Parse interaction type
        type_map = {v.value.lower(): v for v in InteractionType}
        parsed_type = type_map.get(interaction_type.lower(), InteractionType.MEETING)

        # Parse sentiment
        sentiment_map = {v.value.lower(): v for v in Sentiment}
        parsed_sentiment = sentiment_map.get(sentiment.lower(), Sentiment.NEUTRAL)

        # Parse date / time
        parsed_date = date.today()
        if date_str:
            try:
                parsed_date = date.fromisoformat(date_str)
            except ValueError:
                pass

        parsed_time = None
        if time_str:
            try:
                parsed_time = time.fromisoformat(time_str)
            except ValueError:
                pass

        interaction = Interaction(
            hcp_id=hcp.id,
            interaction_type=parsed_type,
            date=parsed_date,
            time=parsed_time,
            attendees=attendees or hcp.name,
            topics_discussed=topics_discussed,
            materials_shared=materials_shared,
            samples_distributed=samples_distributed,
            sentiment=parsed_sentiment,
            outcomes=outcomes,
            follow_up_actions=follow_up_actions,
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        result = _serialize_interaction(interaction)
        result["success"] = True
        result["message"] = f"Interaction #{interaction.id} logged successfully for {hcp.name}."
        return json.dumps(result, default=str)

    except Exception as e:
        db.rollback()
        return json.dumps({"error": str(e), "success": False})
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════
# TOOL 2 — edit_interaction
# ═══════════════════════════════════════════════════════════════════════

@tool
def edit_interaction(
    interaction_id: int,
    field: str,
    new_value: str,
) -> str:
    """Edit a specific field of an existing interaction record.

    Use this tool when the user wants to update or correct a previously
    logged interaction.

    Args:
        interaction_id: The ID of the interaction to edit.
        field: The field to update. Must be one of: interaction_type, date,
               time, attendees, topics_discussed, materials_shared,
               samples_distributed, sentiment, outcomes, follow_up_actions.
        new_value: The new value to set for that field.
    """
    db = _get_db()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return json.dumps({
                "error": f"Interaction #{interaction_id} not found.",
                "success": False,
            })

        allowed_fields = {
            "interaction_type", "date", "time", "attendees",
            "topics_discussed", "materials_shared", "samples_distributed",
            "sentiment", "outcomes", "follow_up_actions",
        }

        if field not in allowed_fields:
            return json.dumps({
                "error": f"Field '{field}' is not editable. Allowed: {', '.join(sorted(allowed_fields))}",
                "success": False,
            })

        # Type-specific parsing
        if field == "interaction_type":
            type_map = {v.value.lower(): v for v in InteractionType}
            parsed = type_map.get(new_value.lower())
            if not parsed:
                return json.dumps({"error": f"Invalid interaction type: '{new_value}'", "success": False})
            setattr(interaction, field, parsed)

        elif field == "sentiment":
            sentiment_map = {v.value.lower(): v for v in Sentiment}
            parsed = sentiment_map.get(new_value.lower())
            if not parsed:
                return json.dumps({"error": f"Invalid sentiment: '{new_value}'", "success": False})
            setattr(interaction, field, parsed)

        elif field == "date":
            try:
                setattr(interaction, field, date.fromisoformat(new_value))
            except ValueError:
                return json.dumps({"error": f"Invalid date format: '{new_value}'. Use YYYY-MM-DD.", "success": False})

        elif field == "time":
            try:
                setattr(interaction, field, time.fromisoformat(new_value))
            except ValueError:
                return json.dumps({"error": f"Invalid time format: '{new_value}'. Use HH:MM.", "success": False})

        else:
            # Text fields — direct assignment
            setattr(interaction, field, new_value)

        db.commit()
        db.refresh(interaction)

        result = _serialize_interaction(interaction)
        result["success"] = True
        result["message"] = f"Updated '{field}' on interaction #{interaction_id}."
        return json.dumps(result, default=str)

    except Exception as e:
        db.rollback()
        return json.dumps({"error": str(e), "success": False})
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════
# TOOL 3 — suggest_followups
# ═══════════════════════════════════════════════════════════════════════

@tool
def suggest_followups(interaction_id: int) -> str:
    """Generate follow-up action suggestions for a logged interaction.

    Retrieves the interaction details and returns context so the LLM can
    generate relevant next-best-action suggestions.

    Args:
        interaction_id: The ID of the interaction to suggest follow-ups for.
    """
    db = _get_db()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return json.dumps({"error": f"Interaction #{interaction_id} not found.", "success": False})

        data = _serialize_interaction(interaction)
        data["success"] = True
        data["instruction"] = (
            "Based on this interaction, generate 2-3 specific, actionable follow-up suggestions. "
            "Consider the topics discussed, sentiment, materials shared, and outcomes. "
            "Format each suggestion as a short actionable phrase."
        )
        return json.dumps(data, default=str)

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════
# TOOL 4 — search_hcp_history
# ═══════════════════════════════════════════════════════════════════════

@tool
def search_hcp_history(hcp_name: str) -> str:
    """Search for an HCP and retrieve their past interaction history.

    Use this tool to look up a Healthcare Professional's profile and
    their past logged interactions, providing context for smarter suggestions.

    Args:
        hcp_name: The name (or partial name) of the HCP to search for.
    """
    db = _get_db()
    try:
        hcps = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name}%")).all()

        if not hcps:
            return json.dumps({
                "error": f"No HCPs found matching '{hcp_name}'.",
                "results": [],
                "success": False,
            })

        results = []
        for hcp in hcps:
            interactions = (
                db.query(Interaction)
                .filter(Interaction.hcp_id == hcp.id)
                .order_by(Interaction.date.desc())
                .limit(10)
                .all()
            )

            results.append({
                "hcp_id": hcp.id,
                "name": hcp.name,
                "specialty": hcp.specialty,
                "institution": hcp.institution,
                "interaction_count": len(interactions),
                "recent_interactions": [_serialize_interaction(i) for i in interactions],
            })

        return json.dumps({"results": results, "success": True}, default=str)

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════
# TOOL 5 — materials_lookup
# ═══════════════════════════════════════════════════════════════════════

@tool
def materials_lookup(search_query: str) -> str:
    """Search the materials catalog by name or description.

    Use this tool to find relevant materials, brochures, or samples
    that match the topics discussed during an interaction.

    Args:
        search_query: Keywords to search for in material names and descriptions.
    """
    db = _get_db()
    try:
        # Search by name OR description
        materials = (
            db.query(Material)
            .filter(
                Material.name.ilike(f"%{search_query}%")
                | Material.description.ilike(f"%{search_query}%")
            )
            .limit(20)
            .all()
        )

        results = [
            {
                "id": m.id,
                "name": m.name,
                "type": m.type.value if m.type else None,
                "description": m.description,
            }
            for m in materials
        ]

        return json.dumps({
            "results": results,
            "count": len(results),
            "success": True,
        })

    finally:
        db.close()


# ── Export all tools as a list ──────────────────────────────────────────

ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    suggest_followups,
    search_hcp_history,
    materials_lookup,
]
