"""
Wikipedia Tool

Allows agents to search Wikipedia for up-to-date information, definitions,
and background context. This is useful for grounding claims in a widely
recognized knowledge base.

Uses the `wikipedia` python library.
"""

import wikipedia
import time
from vera.utils.logging_config import get_tool_logger

logger = get_tool_logger("wikipedia")

def search_wikipedia(query: str) -> str:
    """
    Searches Wikipedia for the given query and returns the summary of the top result.
    
    Use this tool to:
    - Get definitions of terms
    - Find background information on people, places, or events
    - Verify general knowledge claims
    
    Args:
        query (str): The search term (e.g., "Quantum computing", "Warsaw").
        
    Returns:
        str: Summary of the Wikipedia page, or an error message if not found.
    """
    start_time = time.time()
    logger.info(f"Wikipedia search started: '{query}'")
    
    try:
        # Search for the query
        search_results = wikipedia.search(query)
        
        if not search_results:
            logger.warning(f"No Wikipedia results found for '{query}'")
            return f"No Wikipedia results found for '{query}'."
            
        # Get the page for the top result
        # Set language to English for consistency
        # Could be parameterized for multilingual support in future
        wikipedia.set_lang("en")
        
        # Search for the article
        # This may raise DisambiguationError if query is ambiguous
        page = wikipedia.page(query, auto_suggest=True)
        
        # Get summary with specified number of sentences
        # Limiting sentences prevents overwhelming the LLM with too much text
        summary = wikipedia.summary(query, sentences=sentences, auto_suggest=True)
        
        # Return formatted result with title and URL for citation
        return f"**{page.title}**\n\n{summary}\n\nSource: {page.url}"
        
    except wikipedia.exceptions.DisambiguationError as e:
        # Handle disambiguation - return list of options
        # Agent can choose to search for a more specific term
        options = ", ".join(e.options[:5])  # Limit to 5 options
        return f"Disambiguation needed for '{query}'. Options: {options}"
        
    except wikipedia.exceptions.PageError:
        # Handle missing page - inform agent that article doesn't exist
        return f"No Wikipedia article found for '{query}'."
        
    except Exception as e:
        # Handle unexpected errors gracefully
        # Return error message instead of crashing
        return f"Error searching Wikipedia for '{query}': {str(e)}"
