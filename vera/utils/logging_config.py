"""
VERA Logging Configuration

Provides structured logging for the entire VERA system.
Supports both JSON-formatted logs for parsing and human-readable console output.
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Create logs directory structure
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
(LOGS_DIR / "agents").mkdir(exist_ok=True)
(LOGS_DIR / "sessions").mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for easy parsing."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "agent_name"):
            log_data["agent_name"] = record.agent_name
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
            
        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """Format log records with colors for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
    session_id: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for VERA.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Enable colored console output
        enable_file: Enable JSON file logging
        session_id: Optional session ID for session-specific logs
        
    Returns:
        Configured root logger
    """
    # Get root logger
    logger = logging.getLogger("vera")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler (colored, human-readable)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredConsoleFormatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler (JSON, structured)
    if enable_file:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = LOGS_DIR / f"vera_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
        
        # Session-specific log if session_id provided
        if session_id:
            session_log = LOGS_DIR / "sessions" / f"session_{session_id}.log"
            session_handler = logging.FileHandler(session_log, encoding='utf-8')
            session_handler.setLevel(logging.DEBUG)
            session_handler.setFormatter(JSONFormatter())
            logger.addHandler(session_handler)
    
    logger.info(f"VERA logging initialized (level={log_level})")
    return logger


def get_agent_logger(agent_name: str) -> logging.Logger:
    """
    Get a logger for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., "Researcher", "Analyst")
        
    Returns:
        Logger instance for the agent
    """
    logger = logging.getLogger(f"vera.agents.{agent_name}")
    
    # Add agent-specific file handler
    timestamp = datetime.now().strftime("%Y-%m-%d")
    agent_log = LOGS_DIR / "agents" / f"{agent_name.lower()}_{timestamp}.log"
    
    # Check if handler already exists
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == str(agent_log) for h in logger.handlers):
        agent_handler = logging.FileHandler(agent_log, encoding='utf-8')
        agent_handler.setLevel(logging.DEBUG)
        agent_handler.setFormatter(JSONFormatter())
        logger.addHandler(agent_handler)
    
    return logger


def get_tool_logger(tool_name: str) -> logging.Logger:
    """
    Get a logger for a specific tool.
    
    Args:
        tool_name: Name of the tool (e.g., "wikipedia", "google_search")
        
    Returns:
        Logger instance for the tool
    """
    return logging.getLogger(f"vera.tools.{tool_name}")
