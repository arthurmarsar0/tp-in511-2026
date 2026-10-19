"""
LLM utilities: API calls, JSON Schema conversion, tool execution.
"""

import json
from typing import Optional

import msgspec
import requests

# Configuration
LLM_URL = "http://localhost:7700/v1/chat/completions"
MODEL = "gemma-4-E2B-it-Q4_0"


# ============================================================
# JSON Schema conversion (dataclass -> JSON Schema)
# ============================================================


def to_json_schema(cls) -> dict:
    """Convert a dataclass to JSON Schema (without $ref references)."""
    schema = msgspec.json.schema(cls)
    # msgspec returns (schema, definitions) if $ref is used
    schema = schema[0] if isinstance(schema, tuple) else schema

    # If the schema uses $ref, extract the actual definition
    if "$ref" in schema and "$defs" in schema:
        ref_name = schema["$ref"].split("/")[-1]
        return schema["$defs"][ref_name]

    return schema


def to_openai_tool(cls) -> dict:
    """Convert a dataclass to OpenAI 'tool' format.

    The dataclass must have:
    - A docstring (used as the tool description)
    - Fields that define the tool parameters
    - A __call__ method that executes the tool
    """
    return {
        "type": "function",
        "function": {
            "name": cls.__name__,
            "description": (cls.__doc__ or "").strip(),
            "parameters": to_json_schema(cls),
        },
    }


def make_tools(tool_classes: list) -> list:
    """Convert a list of tool dataclasses to OpenAI tool format."""
    return [to_openai_tool(cls) for cls in tool_classes]


def make_registry(tool_classes: list) -> dict:
    """Build a registry mapping tool names to tool classes."""
    return {cls.__name__: cls for cls in tool_classes}


# ============================================================
# LLM API call
# ============================================================


def call_llm(
    messages: list, tools: Optional[list] = None, max_tokens: int = 1024
) -> dict:
    """Call the local LLM server.

    Args:
        messages: List of chat messages (role, content)
        tools: Optional list of OpenAI-formatted tools
        max_tokens: Maximum tokens to generate

    Returns:
        The full API response as a dict
    """
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    response = requests.post(LLM_URL, json=payload, timeout=300)
    response.raise_for_status()
    return response.json()


# ============================================================
# Tool execution
# ============================================================


def execute_tool(tool_call: dict, registry: dict) -> str:
    """Execute a tool called by the LLM.

    Args:
        tool_call: The tool_call object from the LLM response
        registry: Dict mapping tool names to tool classes

    Returns:
        The tool result as a JSON string
    """
    name = tool_call["function"]["name"]
    args = json.loads(tool_call["function"]["arguments"])

    tool_cls = registry.get(name)
    if not tool_cls:
        return json.dumps({"error": f"Tool '{name}' not found"}, ensure_ascii=False)

    try:
        # Instantiate the tool with LLM-provided arguments
        tool_instance = tool_cls(**args)
        result = tool_instance()
        return (
            result
            if isinstance(result, str)
            else json.dumps(result, ensure_ascii=False)
        )
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
