"""
VERA root agent for ADK Web Interface.
This file exports root_agent for discovery by `adk web`.
"""
from .coordinator import get_coordinator_agent

# Export root_agent (required by ADK Web)
root_agent = get_coordinator_agent()
