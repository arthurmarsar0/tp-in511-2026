
from utils import Database, make_sql_tools, make_tools, make_registry, call_llm, execute_tool


SYSTEM_PROMPT = """You are a SQL assistant with access to a SQLite database.

Tools:
- ListTables: list all tables
- DescribeTable: get table structure
- SQLQuery: execute any SQL query

Think step by step. Explore the schema first, then query."""


def agent(question: str, tool_classes: list, max_iterations: int = 5) -> str:
    tools = make_tools(tool_classes)
    registry = make_registry(tool_classes)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
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
            print("Arguments:", tool_call["function"]["arguments"])
            print("Result:", result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result
            })

    return "Max iterations reached"


def main():
    db = Database("library.db")
    tool_classes = make_sql_tools(db)

    questions = [
        "What are the books written after 1970?",
        "Who is the author of 'Dune' and when were they born?",
        "How many books are there per genre?",
        "What is the average rating per publisher?",
        "Which author has written the most books?",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        print("Answer:", agent(question, tool_classes))


if __name__ == "__main__":
    main()
