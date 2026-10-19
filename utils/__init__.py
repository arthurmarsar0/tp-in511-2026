"""
utils package: LLM agent utilities.

This package provides everything needed to build an LLM agent with tools:
- LLM API calls
- JSON Schema conversion (dataclass -> OpenAI tool format)
- Tool execution
- Demo database hydration
- Pre-built tools (Database, SQL tools, Calculator)

Usage:
    from utils import (
        # LLM utilities
        call_llm,
        make_tools,
        make_registry,
        execute_tool,
        # Tools
        Database,
        make_sql_tools,
        Calculator,
        # Data
        init_demo_db,
    )
"""

# LLM utilities
from .llm import (
    LLM_URL,
    MODEL,
    to_json_schema,
    to_openai_tool,
    make_tools,
    make_registry,
    call_llm,
    execute_tool,
)

# Tools
from .tools import Database, make_sql_tools, Calculator

# Data
from .data import init_demo_db, DB_PATH

__all__ = [
    # LLM utilities
    "LLM_URL",
    "MODEL",
    "to_json_schema",
    "to_openai_tool",
    "make_tools",
    "make_registry",
    "call_llm",
    "execute_tool",
    # Tools
    "Database",
    "make_sql_tools",
    "Calculator",
    # Data
    "init_demo_db",
    "DB_PATH",
]
