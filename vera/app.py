"""
VERA Coordinator Agent for ADK Web Interface.
This file exports the coordinator agent for discovery by `adk web`.
"""
from google.adk.apps import App
from .agents import get_coordinator_agent

# Create the coordinator agent
coordinator = get_coordinator_agent()

# Export as App for ADK Web
app = App(
    name="VERA",
    root_agent=coordinator,
)

# Also export the agent directly (some ADK versions expect this)
agent = coordinator
