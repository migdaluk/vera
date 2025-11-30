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
        lang_instruction = """🇵🇱 ABSOLUTNIE KRYTYCZNE WYMAGANIE JĘZYKOWE 🇵🇱

MUSISZ napisać CAŁY raport w języku POLSKIM. To oznacza:

1. WSZYSTKIE nagłówki sekcji w POLSKIM:
   - "# Raport Analizy VERA" (NIE "# VERA Analysis Report")
   - "## 1. Podsumowanie" (NIE "## 1. Executive Summary")
   - "## 2. Ocena Ilościowa" (NIE "## 2. Quantitative Assessment")
   - "## 3. Weryfikacja Faktów" (NIE "## 3. Factual Verification")
   - "## 4. Analiza Potencjalnej Manipulacji" (NIE "## 4. Potential Manipulation Analysis")
   - "## 5. Przegląd Krytyczny" (NIE "## 5. Critical Review")
   - "## 6. Wnioski" (NIE "## 6. Conclusion")

2. WSZYSTKIE podsekcje w POLSKIM:
   - "**Twierdzenie**:" (NIE "**Claim**:")
   - "**Werdykt**:" (NIE "**Verdict**:")
   - "**Źródło**:" (NIE "**Source**:" - TUTAJ WKLEJ URL ZE ZNALEZISK RESEARCHERA LUB BIBLIOTEKARZA)
     - Jeśli URL zawiera "vertexaisearch" lub "grounding-api-redirect", sformatuj go jako: [Link Weryfikacyjny Google](DŁUGI_URL)
   - "**Technika**:" (NIE "**Technique**:")
    - "**Przykład**:" (NIE "**Example**:")

3. CAŁY tekst w POLSKIM:
   - Wszystkie zdania
   - Wszystkie opisy
   - Wszystkie punkty wypunktowane
   - Wszystkie cytaty i przykłady

4. Wartości liczbowe (scores) pozostają bez zmian: "8/10"

PRZYKŁAD POPRAWNEGO NAGŁÓWKA:
"# Raport Analizy VERA

## 1. Podsumowanie
Treść analizy jest wysoce podejrzana..."

JEŚLI NAPISZESZ COKOLWIEK PO ANGIELSKU, TO BŁĄD!
"""
    else:
        lang_instruction = """LANGUAGE REQUIREMENT: 
Write the entire report in ENGLISH language. All headers, text, and labels must be in English."""
    
    # Get current datetime from environment
    import os
    current_datetime = os.environ.get("VERA_CURRENT_DATETIME", "Unknown")

    return Agent(
        name="ReporterAgent",
        model=Gemini(
            model="gemini-2.5-flash"  # Fast model sufficient for report synthesis
        ),
        description="Synthesizes all findings into a comprehensive markdown report",
        
        # Instruction prompt focuses on synthesis and communication
        # Key design: Creates structured markdown report for easy reading
        instruction=f"""You are the Reporter Agent. Your goal is to create a final comprehensive report.

Current date and time: {current_datetime}

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
**Max 4 sentences (up to 80 words).** Brief verdict: Is this content credible, questionable, or false?

## 2. Quantitative Assessment
Display the three scores from ScoringAgent (exact format):
- **Potential Disinformation Level**: X/10
- **Potential Manipulation Level**: X/10
- **Analysis Confidence**: X/10

## 3. Factual Verification
**Max 5 key claims.** For each claim:
- **Claim**: [brief statement]
  - **Verdict**: True/False/Unverified
  - **Source**: [EXTRACT URL from Researcher's findings OR Librarian's Wikipedia links - REQUIRED]
    - If URL contains "vertexaisearch" or "grounding-api-redirect", format it as: [Google Verification Link](THE_LONG_URL)


## 4. Potential Manipulation Analysis
**Up to 5 techniques.** For each:
- **Technique**: [name]
 - **Example**: [one specific quote from text]

## 5. Critical Review
**Max 3 bullet points (50 words total).** Key concerns from Critic about potential biases or gaps.

## 6. Conclusion
**Max 2-3 paragraphs (up 100 words total).** Final verdict with actionable recommendation.

---

**IMPORTANT**: At the very end of the report, add a footer with the current datetime:

*Report generated by VERA on {current_datetime}*

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
