"""
ReAct Search Agent

A ReAct (Reasoning + Acting) agent that uses LangGraph and Tavily Search
to answer questions with real-time web information.

The agent follows a loop: Question → Thought → Action → Observation → Final Answer
"""

from dotenv import load_dotenv

# Load environment variables from .env file (OPENAI_API_KEY, TAVILY_API_KEY)
load_dotenv()

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

# Configure the search tool with a limit on results
tools = [TavilySearch(max_results=3)]

# Initialize the LLM (using gpt-4o-mini for speed and cost efficiency)
llm = ChatOpenAI(model="gpt-4o-mini")

# Create the ReAct agent with a system prompt that encourages tool usage
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt="You are a helpful assistant. Always use the search tool to find current information before answering questions.",
)


def main():
    """
    Main entry point for the ReAct agent.
    
    Invokes the agent with a user query and prints the full conversation flow
    including tool calls and the final answer.
    """
    # Define the user query
    query = "Search for 3 Director of Engineering jobs in South India on LinkedIn and list their details"
    
    # Invoke the agent with the user message
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    
    # Debug: Print all messages to see the full conversation flow
    print("=== DEBUG: All messages ===")
    for i, msg in enumerate(result["messages"]):
        print(f"\n--- Message {i} ({type(msg).__name__}) ---")
        if hasattr(msg, "content"):
            content = str(msg.content)
            print(f"Content: {content[:500] if len(content) > 500 else content}")
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"Tool calls: {msg.tool_calls}")
    
    # Print the final answer
    print("\n=== FINAL ANSWER ===")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
