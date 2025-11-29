import unittest
from unittest.mock import MagicMock
from vera.agents import get_coordinator_agent

class TestAgents(unittest.TestCase):
    def test_get_coordinator_agent(self):
        """Test that the coordinator agent is initialized correctly."""
        # Use a string for the model to satisfy Pydantic validation
        mock_model = "gemini-1.5-flash"
        
        # Create the agent
        coordinator = get_coordinator_agent(mock_model)
        
        # Verify properties
        self.assertEqual(coordinator.name, "coordinator_agent")
        self.assertEqual(len(coordinator.sub_agents), 2)
        
        # Verify sub-agents
        sub_agent_names = [agent.name for agent in coordinator.sub_agents]
        self.assertIn("researcher_agent", sub_agent_names)
        self.assertIn("analyst_agent", sub_agent_names)
        
        # Verify Researcher has tools
        researcher = next(a for a in coordinator.sub_agents if a.name == "researcher_agent")
        self.assertTrue(len(researcher.tools) > 0)

if __name__ == '__main__':
    unittest.main()
