
import json

from utils import (
    Calculator,
    make_tools,
    make_registry,
    call_llm,
    execute_tool,
)


def main():
    tool_classes = [Calculator]
    tools = make_tools(tool_classes)
    registry = make_registry(tool_classes)

    messages = [
        {
            "role": "user",
            "content": "how much is 4! ?"
        }
    ]

    response = call_llm(messages, tools=tools)
    message = response["choices"][0]["message"]

    #print(json.dumps(response, indent = 2, ensure_ascii = False))

    print("=== First LLM response ===")
    print(json.dumps(message, indent=2, ensure_ascii=False))

    messages.append(message)

    tool_calls = message.get("tool_calls") or []

    for tool_call in tool_calls:
        result = execute_tool(tool_call, registry)

        print("\n=== Tool execution ===")
        print("Tool:", tool_call["function"]["name"])
        print("Result:", result)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": result
        })

    response = call_llm(messages, tools=tools)


    final_message = response["choices"][0]["message"]

    print("\n=== Final LLM response ===")
    print(json.dumps(final_message, indent=2, ensure_ascii=False))

    print("\n=== MESSAGES ===")
    print(json.dumps(messages, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
