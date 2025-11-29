"""
VERA - Virtual Evidence & Reality Assessment
Main Streamlit Application

This is the main entry point for the VERA disinformation detection system.
It provides a web UI for users to submit text for analysis and displays
results from the multi-agent investigation workflow.

Architecture:
- Streamlit UI for user interaction
- Google ADK for multi-agent orchestration
- 4 specialized agents: Researcher, Analyst, Critic, Scoring
- Real-time workflow visualization
Main Application Entry Point

This is the Streamlit UI and orchestration layer for the VERA multi-agent system.
It handles:
- User interface (Streamlit)
- Agent initialization and orchestration
- Session management
- Real-time progress updates
- Final report display

Architecture Decision: Manual orchestration instead of SequentialAgent wrapper
to avoid tool conflicts and have full control over agent execution flow.

Author: Łukasz Migda
License: MIT
"""

import streamlit as st
import asyncio
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
import logging

# Google ADK imports - Core framework for multi-agent systems
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# VERA agent imports - Each agent has a specific role in the analysis pipeline
from vera.agents.researcher import get_researcher_agent
from vera.agents.librarian import get_librarian_agent
from vera.agents.analyst import get_analyst_agent
from vera.agents.critic import get_critic_agent
from vera.agents.scoring import get_scoring_agent
from vera.agents.reporter import get_reporter_agent

# VERA utilities
from vera.utils.logging_config import setup_logging

# Initialize logging
setup_logging(log_level="INFO", enable_console=True, enable_file=True)
logger = logging.getLogger("vera.main")


# --- Page Config ---
st.set_page_config(
    page_title="VERA - Virtual Evidence & Reality Assessment",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for "Premium" Look ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    .report-box {
        border: 1px solid #444;
        padding: 20px;
        border-radius: 10px;
        background-color: #262730;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Configuration ---
with st.sidebar:
    st.title("VERA Configuration")
    
    api_key = st.text_input(
        "Google API Key",
        type="password",
        help="Enter your Google API Key (AI Studio). It will not be stored permanently."
    )
    
    language = st.selectbox(
        "Report Language / Język raportu",
        options=["English", "Polski"],
        index=0,
        help="Select the language for VERA's investigation report."
    )
    
    st.markdown("---")
    st.markdown("### About VERA")
    st.info(
        "VERA (Virtual Evidence & Reality Assessment) is a multi-agent system designed to "
        "combat disinformation using OSINT and psychological analysis."
    )

# --- Session State Initialization ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Main Logic ---
st.title("🛡️ VERA: Disinformation Defense System")

input_text = st.text_area(
    "Enter text, claim, or URL to investigate:",
    height=150,
    placeholder="e.g., 'Breaking news: The earth is actually a cube according to new leaked NASA documents...'\n\nOr paste article URL (BETA): https://www.bbc.com/news/article-id",
    help="📝 Paste text directly OR 🌐 paste article URL (BETA feature - may not work with all websites)"
)

def get_workflow_html(active_agent: str = "Coordinator") -> str:
    """Generate minimal HTML for workflow visualization."""
    
    agents = {
        "Coordinator": {"icon": "🧠", "label": "Coordinator"},
        "Researcher": {"icon": "🔍", "label": "Researcher"},
        "Librarian": {"icon": "📚", "label": "Librarian"},
        "Analyst": {"icon": "🧐", "label": "Analyst"},
        "Critic": {"icon": "🛑", "label": "Critic"},
        "Scoring": {"icon": "📊", "label": "Scoring"},
        "Reporter": {"icon": "📝", "label": "Reporter"}
    }
    
    def agent_style(name: str) -> str:
        is_active = name == active_agent
        return f"""
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
            min-width: 100px;
            text-align: center;
            background: {'#e3f2fd' if is_active else 'transparent'};
            border: 1px solid {'#2196f3' if is_active else '#e0e0e0'};
            font-weight: {'600' if is_active else '400'};
            color: {'#1976d2' if is_active else '#666'};
        """
    
    return f"""
    <div style="display: flex; flex-direction: column; align-items: center; gap: 12px; margin: 15px 0;">
        <div style="{agent_style('Coordinator')}">
            {agents['Coordinator']['icon']} {agents['Coordinator']['label']}
        </div>
        <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
            <div style="{agent_style('Researcher')}">
                {agents['Researcher']['icon']} {agents['Researcher']['label']}
            </div>
            <div style="{agent_style('Librarian')}">
                {agents['Librarian']['icon']} {agents['Librarian']['label']}
            </div>
            <div style="{agent_style('Analyst')}">
                {agents['Analyst']['icon']} {agents['Analyst']['label']}
            </div>
            <div style="{agent_style('Critic')}">
                {agents['Critic']['icon']} {agents['Critic']['label']}
            </div>
            <div style="{agent_style('Scoring')}">
                {agents['Scoring']['icon']} {agents['Scoring']['label']}
            </div>
            <div style="{agent_style('Reporter')}">
                {agents['Reporter']['icon']} {agents['Reporter']['label']}
            </div>
        </div>
    </div>
    """


async def run_investigation(text: str, key: str, lang: str):
    """Runs the VERA agent system."""
    investigation_start = time.time()
    
    # Set Environment Variables
    from datetime import datetime
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    os.environ["GOOGLE_API_KEY"] = key
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False" # Use AI Studio
    os.environ["VERA_LANGUAGE"] = lang  # Store language preference
    os.environ["VERA_CURRENT_DATETIME"] = current_time  # Store current datetime for agents
    
    # Generate session ID
    session_id = st.session_state.session_id
    
    logger.info(f"=== Investigation Started ===", extra={
        "session_id": session_id,
        "language": lang,
        "text_length": len(text),
        "timestamp": current_time
    })
    
    # Initialize Agents
    from vera.agents import (
        get_researcher_agent,
        get_librarian_agent,
        get_analyst_agent,
        get_critic_agent,
        get_scoring_agent,
        get_reporter_agent
    )
    
    logger.debug(f"Initializing agent sequence", extra={"session_id": session_id})
    
    # Define the sequence of agents
    agents_sequence = [
        ("Researcher", get_researcher_agent()),
        ("Librarian", get_librarian_agent()),
        ("Analyst", get_analyst_agent()),
        ("Critic", get_critic_agent()),
        ("Scoring", get_scoring_agent()),
        ("Reporter", get_reporter_agent())
    ]
    
    session_service = InMemorySessionService()
    
    # Create Session
    await session_service.create_session(
        app_name="vera_app",
        user_id="streamlit_user",
        session_id=st.session_state.session_id
    )
    
    # Prepare Input
    from datetime import datetime
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    language_instruction = {
        "English": f"[CURRENT DATE/TIME: {current_time}] [LANGUAGE: English] ",
        "Polski": f"[AKTUALNA DATA/CZAS: {current_time}] [JĘZYK: Polski] Odpowiedz w języku polskim. "
    }
    
    # Wrap user input
    prefixed_text = (
        language_instruction.get(lang, "") + 
        "\n<<<USER_INPUT_START>>>\n" + 
        text + 
        "\n<<<USER_INPUT_END>>>"
    )
    
    # Initial User Message
    user_msg = genai_types.Content(
        role="user",
        parts=[genai_types.Part.from_text(text=prefixed_text)]
    )
    
    # Stream Output
    report_container = st.empty()
    full_response = ""
    
    # Visualization
    graph_placeholder = st.empty()
    graph_placeholder.markdown(get_workflow_html("Coordinator"), unsafe_allow_html=True)
    
    # Status message
    status_container = st.empty()
    
    # CSS for spinner
    spinner_html = """
    <style>
    .spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-left: 8px;
        vertical-align: middle;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """
    st.markdown(spinner_html, unsafe_allow_html=True)
    
    status_container.markdown("<div style='text-align: center;'>🕵️ <b>Starting investigation...</b> <span class='spinner'></span></div>", unsafe_allow_html=True)
    
    # --- Manual Orchestration Loop ---
    agent_timings = {}
    try:
        current_input = user_msg
        
        for agent_name, agent_obj in agents_sequence:
            agent_start = time.time()
            logger.info(f"Starting {agent_name}", extra={"session_id": session_id, "agent_name": agent_name})
            
            # Update UI
            graph_placeholder.markdown(get_workflow_html(agent_name), unsafe_allow_html=True)
            
            status_msg = {
                "Researcher": "<b>Researcher</b> is verifying factual claims...",
                "Librarian": "<b>Librarian</b> is checking Wikipedia...",
                "Analyst": "<b>Analyst</b> is analyzing manipulation techniques...",
                "Critic": "<b>Critic</b> is reviewing the findings...",
                "Scoring": "<b>Scoring</b> is calculating metrics...",
                "Reporter": "<b>Reporter</b> is generating final report..."
            }
            status_container.markdown(f"<div style='text-align: center;'>{status_msg.get(agent_name, agent_name)} <span class='spinner'></span></div>", unsafe_allow_html=True)
            
            # Create Runner for this agent
            runner = Runner(
                agent=agent_obj,
                app_name="vera_app",
                session_service=session_service
            )
            
            # Determine input for this agent
            if agent_name == "Researcher":
                agent_input = current_input
            elif agent_name == "Librarian":
                # Librarian also looks at the original text to find terms
                agent_input = genai_types.Content(
                    role="user",
                    parts=[genai_types.Part.from_text(text="Identify terms in the original text that need definition and search Wikipedia.")]
                )
            else:
                # Prompt for next agent to use context from session
                prompts = {
                    "Analyst": "Analyze the text, research findings, and librarian context above for manipulation.",
                    "Critic": "Review the research, librarian report, and analysis above. Provide a critique.",
                    "Scoring": "Based on all findings above, provide scores.",
                    "Reporter": "Synthesize all findings above into the final report."
                }
                agent_input = genai_types.Content(
                    role="user",
                    parts=[genai_types.Part.from_text(text=prompts[agent_name])]
                )

            # Run with timeout
            async def run_agent_step():
                nonlocal full_response
                async for event in runner.run_async(
                    user_id="streamlit_user",
                    session_id=st.session_state.session_id,
                    new_message=agent_input
                ):
                    # Stream text ONLY for Reporter
                    # Check both event.content and event.model_content
                    if agent_name == "Reporter":
                        # Check event.content first
                        if hasattr(event, 'content') and event.content and event.content.parts:
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    full_response += part.text
                                    report_container.markdown(full_response + "▌")
                        
                        # Also check model_content
                        if hasattr(event, 'model_content') and event.model_content and event.model_content.parts:
                            for part in event.model_content.parts:
                                if hasattr(part, 'text') and part.text:
                                    full_response += part.text
                                    report_container.markdown(full_response + "▌")
                                    
            await asyncio.wait_for(run_agent_step(), timeout=300.0)
            
            # Log agent completion
            agent_duration = time.time() - agent_start
            agent_timings[agent_name] = agent_duration
            logger.info(f"Completed {agent_name}", extra={
                "session_id": session_id,
                "agent_name": agent_name,
                "duration_ms": int(agent_duration * 1000)
            })
            
        # Final cleanup
        total_duration = time.time() - investigation_start
        status_container.markdown("<div style='text-align: center;'>✅ <b>Investigation Complete</b></div>", unsafe_allow_html=True)
        report_container.markdown(full_response)
        status_container.success("✅ Investigation complete!")
        
        # Log investigation summary
        logger.info(f"=== Investigation Completed ===", extra={
            "session_id": session_id,
            "total_duration_ms": int(total_duration * 1000),
            "agent_count": len(agents_sequence),
            "report_length": len(full_response)
        })
        
        # Log individual agent timings
        for agent_name, duration in agent_timings.items():
            logger.debug(f"Agent timing: {agent_name} = {duration:.2f}s", extra={
                "session_id": session_id,
                "agent_name": agent_name,
                "duration_ms": int(duration * 1000)
            })
        
    except asyncio.TimeoutError:
        logger.error("Investigation timed out", extra={"session_id": session_id}, exc_info=True)
        status_container.error("⏱️ Investigation timed out.")
    except Exception as e:
        logger.error(f"Investigation failed: {str(e)}", extra={"session_id": session_id}, exc_info=True)
        status_container.error(f"An error occurred during investigation: {str(e)}")
        st.error("""
        **Possible causes:**
        - API rate limiting (too many requests)
        - Very long text requiring extensive analysis
        - Network connectivity issues
        
        **Suggestions:**
        - Try with shorter text
        - Wait a few minutes and try again
        - Check your API quota in Google AI Studio
        """)
        st.stop()
        
    except Exception as e:
        st.error(f"An error occurred during investigation: {e}")

# --- Execution ---
if st.button("🔍 Analyze & Verify"):
    if not input_text.strip():
        st.warning("Please enter text to investigate.")
        st.stop()
    
    if not api_key:
        st.error("Please enter your Google API Key in the sidebar.")
        st.stop()
    
    # Process input (detect URL and extract content if needed)
    from vera.utils import process_input, is_url
    
    with st.spinner("Processing input..."):
        if is_url(input_text.strip()):
            st.info(f"🌐 URL detected (BETA). Extracting content...")
            st.warning("⚠️ URL extraction is in BETA. Some websites may not be fully supported (JavaScript-heavy sites, paywalls, etc.)")
            processed_text, is_from_url = process_input(input_text)
            
            if not is_from_url:
                # Error occurred during extraction
                st.error(processed_text)
                st.stop()
            else:
                st.success(f"✅ Content extracted successfully! ({len(processed_text)} characters)")
        else:
            processed_text = input_text
    
    # Generate new session ID for fresh analysis
    st.session_state.session_id = str(uuid.uuid4())
    
    # Run investigation with processed text
    asyncio.run(run_investigation(processed_text, api_key, language))
