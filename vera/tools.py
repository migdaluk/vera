import os
from typing import List, Dict, Any
from datetime import datetime
from googleapiclient.discovery import build

def get_current_datetime() -> str:
    """
    Returns the current date and time in ISO 8601 format.
    
    This tool provides agents with the current timestamp to avoid confusion
    about dates in articles or events.
    
    Returns:
        str: Current date and time in format: "YYYY-MM-DD HH:MM:SS UTC"
    
    Example:
        "2024-11-19 18:54:00 UTC"
    """
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S UTC")

def search_tool(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a web search using Google Custom Search API to verify facts or gather information.
    
    Requires 'GOOGLE_API_KEY' and 'GOOGLE_CSE_ID' environment variables to be set.

    Args:
        query (str): The search query string. Be specific to get the best results.
        max_results (int, optional): The maximum number of results to return. Defaults to 5.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a search result
        containing 'title', 'href' (URL), and 'body' (snippet).
    """
    results = []
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        print("DEBUG: Missing API Key or CSE ID")
        return [{"error": "Missing GOOGLE_API_KEY or GOOGLE_CSE_ID environment variables."}]

    try:
        print(f"DEBUG: Searching for '{query}' with CX={cse_id[:5]}...")
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cse_id, num=max_results).execute()
        
        items = res.get("items", [])
        print(f"DEBUG: Found {len(items)} results.")
        for item in items:
            results.append({
                "title": item.get("title", ""),
                "href": item.get("link", ""),
                "body": item.get("snippet", "")
            })
            
    except Exception as e:
        print(f"Error during Google search: {e}")
        return [{"error": str(e)}]

    return results
