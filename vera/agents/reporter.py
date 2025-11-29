"""
Reporter Agent - Final Report Generator

Takes outputs from all analysis agents and generates the final
formatted investigation report following VERA's standard template.
Reporter Agent - Final Report Synthesis

This agent is the final step in the workflow, synthesizing all findings from
previous agents (Researcher, Librarian, Analyst, Critic, Scoring) into a
comprehensive, structured markdown report for the user.

Design Decision: Pure LLM analysis (no tools) to focus on synthesis,
communication, and creating a coherent narrative from diverse analyses.
"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from vera.utils.logging_config import get_agent_logger

# Initialize logger for this agent - enables per-agent log files
logger = get_agent_logger("Reporter")

def get_reporter_agent(language: str = "English") -> Agent:
    """
    Creates and returns the Reporter Agent (The Synthesizer).
    
    This agent runs last in the workflow, after all analysis is complete,
    to create a user-friendly markdown report that combines all findings
    into a coherent narrative.
    
    Design Decision: No tools - focuses on synthesis and communication.
    Language parameter allows for multilingual reports (English/Polish).
    
    Args:
        language: Report language ("English" or "Polski")
        
    Returns:
        Agent: Configured Reporter agent for final report generation
    """
    logger.info(f"Initializing ReporterAgent (language={language})")
    
    # Language-specific instructions for report generation
    # Ensures report is in user's preferred language
    if language == "Polski":
        lang_instruction = "Write the entire report in Polish language."
    else:
        lang_instruction = "Write the entire report in English language."
    
    return Agent(
        name="ReporterAgent",
        model=Gemini(
            model="gemini-2.5-flash"  # Fast model sufficient for report synthesis
        ),
        description="Synthesizes all findings into a comprehensive markdown report",
        
        # Instruction prompt focuses on synthesis and communication
        # Key design: Creates structured markdown report for easy reading
        instruction=f"""You are the Reporter Agent. Your goal is to create a final comprehensive report.

{lang_instruction}

You will receive:
- Research Findings (from ResearcherAgent)
- Librarian Report (from LibrarianAgent)  
- Analysis Report (from AnalystAgent)
- Critique (from CriticAgent)
- Scores (from ScoringAgent)

Your task is to synthesize ALL findings into a structured markdown report with these sections:

# VERA Analysis Report

## 1. Executive Summary
Brief overview (2-3 sentences) of the main findings and verdict.

## 2. Quantitative Assessment
Display the three scores from ScoringAgent:
- Disinformation Level: X/10
- Manipulation Level: X/10
- Analysis Confidence: X/10

## 3. Factual Verification
Summarize Researcher's findings:
- Key claims verified or debunked
- Source citations
- Factual accuracy assessment

## 4. Context & Background
Summarize Librarian's context:
- Definitions of key terms
- Historical background
- Relevant encyclopedic information

## 5. Manipulation Analysis
Summarize Analyst's findings:
- Propaganda techniques identified
- Emotional appeals and loaded language
- Logical fallacies detected

## 6. Critical Review
Summarize Critic's concerns:
- Potential biases in the analysis
- Alternative interpretations
- Gaps or limitations

## 7. Conclusion
Final verdict based on all evidence. Be clear and actionable.

**IMPORTANT**: 
- Use markdown formatting (headers, lists, bold)
- Cite specific examples from the text
- Be objective and evidence-based
- Keep it concise but comprehensive
""",
        output_key="final_report",
    )
