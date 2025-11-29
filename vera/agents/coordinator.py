"""
Coordinator Agent - Main Orchestrator

The Coordinator Agent manages the entire VERA investigation workflow.
It orchestrates four sub-agents in sequence:
1. ResearcherAgent - Verifies factual claims using Google Search
2. AnalystAgent - Analyzes manipulation and propaganda techniques
3. CriticAgent - Reviews findings for bias and errors
4. ScoringAgent - Assigns quantitative scores (1-10)

The Coordinator synthesizes all reports into a comprehensive assessment
with security features to prevent prompt injection attacks.

Model: gemini-2.5-flash
Tools: AgentTool (for sub-agents)
"""

from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.genai import types
from .researcher import get_researcher_agent
from .analyst import get_analyst_agent
from .critic import get_critic_agent
from .scoring import get_scoring_agent
from .reporter import get_reporter_agent


def get_coordinator_agent() -> SequentialAgent:
    """
    Creates and returns the Coordinator as a SequentialAgent.
    This ensures sub-agents are called in strict sequential order and can use their own tools.
    """
    
    # Initialize sub-agents
    researcher_agent = get_researcher_agent()
    analyst_agent = get_analyst_agent()
    critic_agent = get_critic_agent()
    scoring_agent = get_scoring_agent()
    reporter_agent = get_reporter_agent()

    return SequentialAgent(
        name="CoordinatorAgent",
        description="VERA Coordinator that orchestrates investigation workflow sequentially",
        sub_agents=[researcher_agent, analyst_agent, critic_agent, scoring_agent, reporter_agent]
    )
