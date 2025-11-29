"""
Current DateTime Tool

Provides the current date and time in UTC for agents to verify
temporal aspects of events (past, present, or future).

Security: This function cannot be manipulated by user input.
It always returns the real system time.

Note: Due to ADK limitations with custom tools when agents are used
as AgentTool, this is currently passed via environment variable
(VERA_CURRENT_DATETIME) instead of as a callable tool.
"""

from datetime import datetime


def get_current_datetime() -> str:
    """
    Retrieves the current date and time in UTC from the system clock.
    
    This tool returns the REAL current date and time and cannot be manipulated.
    Use this tool to verify if events mentioned in the text are in the past, 
    present, or future.
    
    IMPORTANT: This tool does NOT accept any parameters. It always returns 
    the actual system time.
    
    Returns:
        str: Current date and time in format 'YYYY-MM-DD HH:MM:SS UTC'
        
    Example:
        >>> get_current_datetime()
        '2025-11-28 13:40:00 UTC'
        
    Use cases:
        - Verify if a news event date is recent or historical
        - Check if claims about "yesterday" or "last week" are accurate
        - Identify anachronisms or temporal inconsistencies in text
    """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
