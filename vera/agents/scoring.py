"""
Scoring Agent - Quantitative Assessment

This agent synthesizes all previous findings (Researcher, Librarian, Analyst,
Critic) into objective quantitative scores on a 1-10 scale. It provides
standardized metrics for decision-making.

Design Decision: Pure LLM analysis (no tools) to focus on synthesis and
scoring based on all available context from previous agents.
"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from vera.utils.logging_config import get_agent_logger

# Initialize logger for this agent - enables per-agent log files
logger = get_agent_logger("Scoring")

def get_scoring_agent() -> Agent:
    """
    Creates and returns the Scoring Agent (The Quantifier).
    
    This agent runs fifth in the workflow, after all analysis is complete,
    to provide objective quantitative scores that summarize the findings.
    
    Design Decision: No tools - synthesizes all previous agent outputs into
    three key metrics (Disinformation Level, Manipulation Level, Confidence).
    Provides standardized scoring for consistent decision-making.
    
    Returns:
        Agent: Configured Scoring agent for quantitative assessment
    """
    logger.info("Initializing ScoringAgent")
    
    return Agent(
        name="ScoringAgent",
        model=Gemini(
            model="gemini-2.5-flash"  # Fast model sufficient for scoring
        ),
        description="Provides quantitative scores based on all findings",
        
        # Instruction prompt focuses on objective scoring
        # Key design: Three metrics provide comprehensive quantitative assessment
        instruction="""You are the Scoring Agent. Your goal is to provide objective scores.

Based on ALL previous findings (Researcher, Librarian, Analyst, Critic), assign three scores (1-10):

1. **Disinformation Level** (1=truthful, 10=completely false)
   - Consider factual accuracy from Researcher
   - Weight by source reliability
   
2. **Manipulation Level** (1=neutral, 10=highly manipulative)
   - Consider techniques identified by Analyst
   - Weight by severity and intent

3. **Analysis Confidence** (1=uncertain, 10=very confident)
   - Consider source quality and consensus
   - Account for Critic's concerns

Provide brief justification for each score. Be objective and consistent.""",
        
        # No tools - pure synthesis
        # Design Decision: Scoring requires holistic understanding of all findings,
        # which LLM excels at without external tools
        tools=[],
    )
