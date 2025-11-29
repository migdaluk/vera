"""
Script to visualize VERA's agent architecture as a graph.
Generates a visual representation of the multi-agent system.
"""
import os
from vera.agents import get_coordinator_agent

# Suppress API key requirement for visualization
os.environ["GOOGLE_API_KEY"] = "dummy_key_for_visualization"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

def visualize_vera():
    """Generate and save VERA's agent graph visualization."""
    print("Initializing VERA agent system...")
    coordinator = get_coordinator_agent()
    
    print("Generating agent graph visualization...")
    
    # ADK provides visualization utilities
    try:
        from google.adk.visualization import visualize_agent_graph
        
        # Generate the graph
        graph = visualize_agent_graph(coordinator)
        
        # Save to file
        output_file = "vera_agent_graph.html"
        with open(output_file, "w") as f:
            f.write(graph)
        
        print(f"✅ Graph saved to: {output_file}")
        print("Open this file in your browser to view the visualization.")
        
    except ImportError:
        print("⚠️  Visualization module not found in google.adk")
        print("Trying alternative method...")
        
        # Alternative: Print agent structure
        print("\n=== VERA Agent Architecture ===")
        print(f"Root Agent: {coordinator.name}")
        print(f"Model: {coordinator.model}")
        print(f"Tools: {[tool.name if hasattr(tool, 'name') else str(tool) for tool in coordinator.tools]}")
        
        if hasattr(coordinator, 'sub_agents'):
            print(f"\nSub-agents: {len(coordinator.sub_agents)}")
            for agent in coordinator.sub_agents:
                print(f"  - {agent.name}")
                if hasattr(agent, 'tools'):
                    print(f"    Tools: {[tool.name if hasattr(tool, 'name') else str(tool) for tool in agent.tools]}")

if __name__ == "__main__":
    visualize_vera()
