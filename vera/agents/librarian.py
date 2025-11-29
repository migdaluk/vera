"""
Librarian Agent - Wikipedia Specialist

Uses Wikipedia to find definitions, background information, and historical context.
Librarian Agent - Provides encyclopedic context via Wikipedia

This agent specializes in finding background information, definitions, and
historical context using Wikipedia. It complements the Researcher agent by
providing depth rather than real-time news.

Design Decision: Separated from Researcher to avoid tool conflicts between
Google Search (Grounding API) and Wikipedia in a single agent.
"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
from .wikipedia_tool import search_wikipedia
from vera.utils.logging_config import get_agent_logger

# Initialize logger for this agent - enables per-agent log files
logger = get_agent_logger("Librarian")

def get_librarian_agent() -> Agent:
    """
    Creates and returns the Librarian Agent (The Context Provider).
    
    This agent runs second in the workflow, after Researcher, to provide
    encyclopedic context and definitions for terms mentioned in the text.
    
    Design Decision: Uses only Wikipedia to provide stable, encyclopedic
    knowledge. Avoids real-time news to prevent overlap with Researcher.
    
    Returns:
        Agent: Configured Librarian agent with Wikipedia search tool
    """
    logger.info("Initializing LibrarianAgent")
    
    # Configure retry logic for API calls
    # Same configuration as Researcher for consistency
    retry_config = types.HttpRetryOptions(
        attempts=5,  # Max 5 retries before failing
        exp_base=7,  # Exponential backoff: 7^n seconds
        initial_delay=1,  # Start with 1 second delay
        http_status_codes=[429, 500, 503, 504],  # Retry on rate limit and server errors
    )
    
    return Agent(
        name="LibrarianAgent",
        model=Gemini(
            model="gemini-2.5-flash",  # Fast, cost-effective model for context retrieval
            retry_options=retry_config
        ),
        description="Provides context and definitions using Wikipedia",
        
        # Instruction prompt focuses on encyclopedic knowledge
        # Key design: Complements Researcher by providing depth, not breadth
        instruction="""You are the Librarian Agent. Your goal is to provide encyclopedic context.

Responsibilities:
1. Identify key terms, concepts, or entities in the text that need context.
2. Use `search_wikipedia` to find definitions, background info, and historical context.
3. Focus on providing depth and understanding, not real-time news.
4. Provide a 'Librarian Report' with Wikipedia summaries.

Be concise but informative. Focus on terms that help understand the text better.""",
        
        # Tools: Only Wikipedia to avoid conflicts
        # Design Decision: Custom tool implementation for better control over results
        tools=[search_wikipedia],
    )
