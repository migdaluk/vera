# VERA - Walkthrough

## 1. System Overview

VERA (Virtual Evidence & Reality Assessment) is a 6-agent system designed to detect disinformation and manipulation.

### Agents
1. **Researcher**: Fact-checks claims using Google Search (Grounding API).
2. **Librarian**: Provides context using Wikipedia.
3. **Analyst**: Detects manipulation techniques (pure LLM).
4. **Critic**: Reviews findings for bias and errors (pure LLM).
5. **Scoring**: Calculates objective scores (1-10) (pure LLM).
6. **Reporter**: Synthesizes the final report in English or Polish.

## 2. Installation

Ensure you have Python 3.11+ installed.

```bash
pip install -r requirements.txt
```

## 3. Running Locally

To start the VERA interface:

```bash
streamlit run vera/main.py
```

## 4. Usage

1.  **API Key:** Enter your Google API Key (AI Studio) in the sidebar.
2.  **Language:** Select "English" or "Polski".
3.  **Input:** Paste text or a URL (BETA) into the main input box.
4.  **Analyze:** Click "Analyze & Verify".
5.  **Results:** VERA will display real-time progress of each agent and generate a final markdown report with a timestamp.


## 5. Key Features

- **Sequential Workflow**: Manual orchestration ensures robust execution.
- **Multilingual Support**: Full report generation in English and Polish.
- **Source Verification**: Integration with Google Search and Wikipedia.
- **Transparency**: Timestamped reports and explicit source citations.
- **Safety**: Comprehensive disclaimers and error handling.
