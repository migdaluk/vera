"""
Analyst Agent - Propaganda & Manipulation Expert

Analyzes text for signs of manipulation, propaganda, and emotional triggers.
Identifies rhetorical devices, propaganda techniques, sentiment, and intent.

Key responsibilities:
- Detect loaded language and emotional appeals
- Identify propaganda techniques (bandwagon, fear-mongering, etc.)
- Analyze sentiment and tone
- Assess the intent behind the message

Model: gemini-2.5-flash
Output: Detailed analysis report with examples
"""

"""
Analyst Agent - Detects manipulation techniques and propaganda

This agent specializes in identifying psychological manipulation, propaganda
techniques, emotional appeals, and logical fallacies in text. It provides
qualitative analysis of how the text attempts to influence readers.

Design Decision: Pure LLM analysis (no tools) to focus on reasoning and
pattern recognition rather than fact-checking.
"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
from vera.utils.logging_config import get_agent_logger

# Initialize logger for this agent - enables per-agent log files
logger = get_agent_logger("Analyst")


def get_analyst_agent() -> Agent:
    """
    Creates and returns the Analyst Agent (The Manipulation Detector).
    
    This agent runs third in the workflow, after Researcher and Librarian,
    to analyze manipulation techniques using the factual context provided
    by previous agents.
    
    Design Decision: No tools - relies on LLM's reasoning capabilities to
    identify patterns of manipulation, propaganda, and logical fallacies.
    
    Returns:
        Agent: Configured Analyst agent for manipulation detection
    """
    logger.info("Initializing AnalystAgent")
    
    return Agent(
        name="AnalystAgent",
        model=Gemini(
            model="gemini-2.5-flash"  # Fast model sufficient for pattern recognition
        ),
        description="Analyzes manipulation techniques and propaganda",
        
        # Instruction prompt focuses on psychological manipulation
        # Key design: Builds on Researcher's facts to identify how truth is twisted
        instruction="""You are the Analyst Agent. Your goal is to identify manipulation techniques.

Responsibilities:
1. Identify rhetorical devices (loaded language, appeals to emotion, false dichotomies).
2. Detect propaganda techniques (bandwagon, fear-mongering, scapegoating, etc.).
3. Analyze sentiment and tone.
4. Assess the intent behind the message.

Provide a detailed analysis with examples from the text.""",

    )
