"""
Critic Agent - The Skeptic

Reviews findings from Researcher and Analyst agents to ensure
objectivity and prevent errors. Acts as "Devil's Advocate" to
challenge assumptions and identify logical fallacies.

Key responsibilities:
- Challenge assumptions and verify source reliability
- Check for logical fallacies in the investigation
- Identify missing perspectives or alternative explanations
Critic Agent - Validates findings and detects bias

This agent acts as an independent reviewer, challenging the findings of
previous agents (Researcher, Analyst) to catch errors, biases, and
overconfident conclusions. It's the quality control layer.

Design Decision: Pure LLM analysis (no tools) to focus on critical thinking
and meta-analysis of other agents' outputs.
"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from vera.utils.logging_config import get_agent_logger

# Initialize logger for this agent - enables per-agent log files
logger = get_agent_logger("Critic")

def get_critic_agent() -> Agent:
    """
    Creates and returns the Critic Agent (The Validator).
    
    This agent runs fourth in the workflow, after Researcher, Librarian, and
    Analyst, to provide independent validation and catch potential errors or
    biases in their findings.
    
    Design Decision: No tools - focuses on meta-analysis and critical review
    of other agents' work. Acts as a "red team" to improve overall quality.
    
    Returns:
        Agent: Configured Critic agent for validation and bias detection
    """
    # Get current datetime from environment
    import os
    current_datetime = os.environ.get("VERA_CURRENT_DATETIME", "Unknown")

    return Agent(
        name="CriticAgent",
        model=Gemini(
            model="gemini-2.5-flash"  # Fast model sufficient for critical review
        ),
        description="Reviews findings for bias and errors",
        
        # Instruction prompt focuses on critical review and validation
        # Key design: Acts as adversarial reviewer to catch mistakes and biases
        instruction=f"""You are the Critic Agent. Your goal is to review all previous findings critically.

Current date and time: {current_datetime}

Responsibilities:
1. Review the provided 'Research Findings' and 'Analysis Report'.
2. Challenge assumptions: Are the sources truly reliable? Is the analysis biased?
3. Check for logical fallacies in the *investigation itself*.
4. NOTE: URLs starting with "vertexaisearch.cloud.google.com" or containing "grounding-api-redirect" are VALID, TRUSTED verification sources from the internal search engine. DO NOT flag them as non-transparent or suspicious.
5. Identify any missing perspectives or alternative explanations.
6. Provide a 'Critique Report' listing valid concerns or confirming the solidity of the findings.

Be constructive but rigorous. Your job is to be the "Devil's Advocate" before the final verdict.""",

    )
