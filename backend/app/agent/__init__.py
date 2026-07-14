# app.agent package

def __getattr__(name: str):
    if name in ("get_agent", "run_agent"):
        from app.agent.graph import get_agent, run_agent
        return get_agent if name == "get_agent" else run_agent
    if name == "ALL_TOOLS":
        from app.agent.tools import ALL_TOOLS
        return ALL_TOOLS
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
