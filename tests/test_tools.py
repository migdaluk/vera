import unittest
from unittest.mock import MagicMock, patch
import os
from vera.tools import search_tool

class TestTools(unittest.TestCase):
    @patch("vera.tools.build")
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key", "GOOGLE_CSE_ID": "test_cse"})
    def test_search_tool_basic(self, mock_build):
        """Test that search tool returns results for a simple query using mocked Google API."""
        # Mock the service.cse().list().execute() chain
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_list = MagicMock()
        mock_service.cse().list.return_value = mock_list
        
        # Mock response
        mock_list.execute.return_value = {
            "items": [
                {
                    "title": "Test Title",
                    "link": "http://example.com",
                    "snippet": "Test Snippet"
                }
            ]
        }

        results = search_tool("Python programming language", max_results=1)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Title")
        self.assertEqual(results[0]["href"], "http://example.com")
        self.assertEqual(results[0]["body"], "Test Snippet")

    def test_search_tool_missing_keys(self):
        """Test that search tool returns error if keys are missing."""
        # Ensure env vars are cleared for this test
        with patch.dict(os.environ, {}, clear=True):
            results = search_tool("query")
            self.assertIn("error", results[0])
            self.assertIn("Missing GOOGLE_API_KEY", results[0]["error"])

if __name__ == '__main__':
    unittest.main()
