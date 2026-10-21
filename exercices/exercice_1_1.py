
import json

from utils import Calculator, make_tools, make_registry, call_llm


def main():
    tool_classes = [Calculator]

    tools = make_tools(tool_classes)
    registry = make_registry(tool_classes)

    print("=== Tools schema ===")
    print(json.dumps(tools, indent=2, ensure_ascii=False))

    print("\n=== Tools register ===")
    print(registry)

    messages = [
        {
            "role": "user",
            "content": "What is 15 times 8?"
        }
    ]

    response = call_llm(messages, tools=tools)

    message = response["choices"][0]["message"]

    print("\n=== LLMs answer ===")
    print(json.dumps(message, indent=2, ensure_ascii=False))

    tool_calls = message.get("tool_calls", [])

    if tool_calls:
        print("\n=== Solicited tools ===")
        for tool_call in tool_calls:
            print("Name:", tool_call["function"]["name"])
            print("Arguments:", tool_call["function"]["arguments"])
    else:
        print("\nLLM didnt requested any tool.")


if __name__ == "__main__":
    main()
