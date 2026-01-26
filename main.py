from dotenv import load_dotenv

load_dotenv()

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch


tools = [TavilySearch(max_results=3)]
llm = ChatOpenAI(model="gpt-4o-mini")

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt="You are a helpful assistant. Always use the search tool to find current information before answering questions.",
)


def main():
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Search for 3 Director of Engineering jobs in South India on LinkedIn and list their details"}]}
    )
    # Debug: Print all messages to see the full conversation flow
    print("=== DEBUG: All messages ===")
    for i, msg in enumerate(result["messages"]):
        print(f"\n--- Message {i} ({type(msg).__name__}) ---")
        if hasattr(msg, 'content'):
            print(f"Content: {msg.content[:500] if len(str(msg.content)) > 500 else msg.content}")
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"Tool calls: {msg.tool_calls}")
    print("\n=== FINAL ANSWER ===")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
