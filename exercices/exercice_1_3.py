import json
from dataclasses import dataclass

from utils import make_tools, make_registry, call_llm, execute_tool

@dataclass
class WordCounter:
    """Count the number of words in a given text."""

    text: str

    def __call__(self) -> int:
        return len(self.text.split())


def main():
    tool_classes = [WordCounter]

    tools = make_tools(tool_classes)
    registry = make_registry(tool_classes)

    print("=== Tools schema ===")
    print(json.dumps(tools, indent=2, ensure_ascii=False))

    messages = [
        {
            "role": "user",
            "content": "How many words are in 'Hello world, this is a test'?"
        }
    ]

    response = call_llm(messages, tools=tools)
    message = response["choices"][0]["message"]

    print("\n=== First LLM response ===")
    print(json.dumps(message, indent=2, ensure_ascii=False))

    messages.append(message)

    tool_calls = message.get("tool_calls") or []

    for tool_call in tool_calls:
        result = execute_tool(tool_call, registry)

        print("\n=== Tool execution ===")
        print("Result:", result)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": result
        })

    if tool_calls:
        response = call_llm(messages, tools=tools)
        final_message = response["choices"][0]["message"]

        print("\n=== Final LLM response ===")
        print(final_message.get("content"))


if __name__ == "__main__":
    main()
