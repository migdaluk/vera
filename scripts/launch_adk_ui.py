"""
Launch ADK Web Interface for VERA.
This provides an interactive UI for testing, debugging, and visualizing the agent graph.
"""
import os
from google.adk.apps import App
from vera.agents import get_coordinator_agent

# Set up environment
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")

def main():
    """Launch the ADK Web Interface for VERA."""
    print("Initializing VERA agent system...")
    coordinator = get_coordinator_agent()
    
    print("Creating ADK App...")
    # Correct App initialization based on ADK API
    app = App(
        name="vera_app",
        root_agent=coordinator,
    )
    
    print("\n" + "="*60)
    print("🚀 Launching ADK Web Interface for VERA")
    print("="*60)
    print("\nThe web interface will open in your browser.")
    print("You can use it to:")
    print("  - Chat with VERA interactively")
    print("  - View the agent graph visualization")
    print("  - Debug agent interactions")
    print("  - Test different inputs")
    print("\nPress Ctrl+C to stop the server.")
    print("="*60 + "\n")
    
    # Launch the web interface
    app.run()

if __name__ == "__main__":
    main()

