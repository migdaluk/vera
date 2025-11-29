from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types
from .wikipedia_tool import search_wikipedia
from vera.utils.logging_config import get_agent_logger

# Initialize logger for this agent - enables per-agent log files
logger = get_agent_logger("Researcher")

def get_researcher_agent() -> Agent:
    """
    Creates and returns the Researcher Agent (The Fact-Checker).
    
    This agent is responsible for verifying factual claims using Google Search.
    It's the first agent in the sequential workflow, providing the foundation
    for all subsequent analysis.
    
    Design Decision: Uses only google_search (not Wikipedia) to avoid tool conflicts.
    Wikipedia functionality is handled by separate LibrarianAgent.
    
    Returns:
        Agent: Configured Researcher agent with Google Search tool
    """
    logger.info("Initializing ResearcherAgent")
    
    # Get current datetime from environment for temporal context
    # This is set dynamically in main.py to ensure agents know "today's date"
    import os
    current_datetime = os.environ.get("VERA_CURRENT_DATETIME", "Unknown")
    
    # Configure retry logic for API calls
    # Exponential backoff with base 7 to handle rate limits gracefully
    retry_config = types.HttpRetryOptions(
        attempts=5,  # Max 5 retries before failing
        exp_base=7,  # Exponential backoff: 7^n seconds
        initial_delay=1,  # Start with 1 second delay
        http_status_codes=[429, 500, 503, 504],  # Retry on rate limit and server errors
    )
    
    return Agent(
        name="ResearcherAgent",
        model=Gemini(
            model="gemini-2.5-flash",  # Fast, cost-effective model for fact-checking
            retry_options=retry_config
        ),
        description="Verifies claims using Google Search and Wikipedia",
        
        # Instruction prompt defines agent's behavior and responsibilities
        # Key design: Explicit temporal context prevents hallucinations about dates
        instruction=f"""You are the Researcher Agent. Your goal is to verify factual claims.

IMPORTANT: The current date and time is {current_datetime}. Use this for temporal context.

Responsibilities:
1. Identify key factual claims in the text.
2. Use `google_search` to find reliable sources (news, official reports).
3. Compare claims with evidence found.
4. Provide a 'Research Findings' report with source citations.

Be objective and thorough. If evidence is conflicting, note it.""",
        
        # Tools: Only google_search to avoid conflicts
        # Design Decision: Separated Wikipedia into LibrarianAgent for reliability
        tools=[google_search],
    )
