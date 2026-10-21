
from utils import (
    Calculator,
    make_tools,
    make_registry,
    call_llm,
    execute_tool,
)


def agent(question: str, max_iterations: int = 5) -> str:
    tool_classes = [Calculator]

    tools = make_tools(tool_classes)
    registry = make_registry(tool_classes)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Use the Calculator tool for mathematical operations."
        },
        {
            "role": "user",
            "content": question
        }
    ]

    for i in range(max_iterations):
        print(f"\n=== Iteration {i + 1} ===")

        response = call_llm(messages, tools=tools)
        message = response["choices"][0]["message"]

        messages.append(message)

        tool_calls = message.get("tool_calls") or []

        if not tool_calls:
            return message.get("content") or ""

        for tool_call in tool_calls:
            result = execute_tool(tool_call, registry)

            print("Tool:", tool_call["function"]["name"])
            #adicionar o reasoning
            print("Result:", result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result
            })

    return "Max iterations reached"


def main():
    questions = [
        "How much is 10! ? please use the tool Calculator",
        "What is 15 times 8?",
        "Calculate (12 + 8) * 3.",
        "What is 100 divided by 4, plus 10?"
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        print("Answer:", agent(question))


if __name__ == "__main__":
    main()
