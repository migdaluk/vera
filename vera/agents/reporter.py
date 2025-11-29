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
        lang_instruction = """CRITICAL LANGUAGE REQUIREMENT: 
Write the ENTIRE report in POLISH language. This includes:
- ALL section headers (e.g., "# Raport Analizy VERA", "## 1. Podsumowanie Wykonawcze")
- ALL subsection headers
- ALL body text
- ALL bullet points
- ALL labels (e.g., "Poziom Dezinformacji:", "Źródła:")
- Everything must be in Polish - NO English words except proper nouns

Example headers in Polish:
# Raport Analizy VERA
## 1. Podsumowanie Wykonawcze
## 2. Ocena Ilościowa
## 3. Weryfikacja Faktów
## 4. Kontekst i Tło
## 5. Analiza Manipulacji
## 6. Przegląd Krytyczny
## 7. Wnioski"""
    else:
        lang_instruction = """LANGUAGE REQUIREMENT: 
Write the entire report in ENGLISH language. All headers, text, and labels must be in English."""
    
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

Your task is to synthesize ALL findings into a CONCISE, SCANNABLE markdown report with these sections:

# VERA Analysis Report

## 1. Executive Summary
**Max 3 sentences (50 words).** Brief verdict: Is this content credible, questionable, or false?

## 2. Quantitative Assessment
Display the three scores from ScoringAgent (exact format):
- **Disinformation Level**: X/10
- **Manipulation Level**: X/10
- **Analysis Confidence**: X/10

## 3. Factual Verification
**Max 5 key claims.** For each claim:
- **Claim**: [brief statement]
- **Verdict**: True/False/Unverified
- **Source**: [1-2 sources max]

## 4. Context & Background
**Max 3 bullet points (50 words total).** Key definitions or historical context from Librarian.

## 5. Manipulation Analysis
**Max 5 techniques.** For each:
- **Technique**: [name]
- **Example**: [one specific quote from text]

## 6. Critical Review
**Max 3 bullet points (50 words total).** Key concerns from Critic about potential biases or gaps.

## 7. Conclusion
**Max 2 paragraphs (100 words total).** Final verdict with actionable recommendation.

---

**CRITICAL FORMATTING RULES:**
- Use markdown: headers (##), bold (**text**), bullet points (-)
- Be CONCISE - respect word limits strictly
- Use specific quotes/examples, not generalizations
- Make it SCANNABLE - busy readers should grasp it in 30 seconds
- NO preamble, NO meta-commentary, ONLY the report
""",
        output_key="final_report",
    )
