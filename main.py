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

from pydantic import BaseModel, Field
from typing import List

class Source(BaseModel):    
    """Schema for a source used by the agent"""
    url: str = Field(description="The URL of the source")
    

class AgentResponse(BaseModel):
    """Schema for agent response with answer and sources"""
    answer: str = Field(description="The agent's answer to the query")
    sources: List[Source] = Field(default_factory=list, description="List of sources used to generate the answer")

# Configure the search tool with a limit on results
tools = [TavilySearch(max_results=3)]

# Initialize the LLM (using gpt-4o-mini for speed and cost efficiency)
llm = ChatOpenAI(model="gpt-4o-mini")

# Create the ReAct agent with a system prompt that encourages tool usage
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt="You are a helpful assistant. Always use the search tool to find current information before answering questions.",
    response_format=AgentResponse,
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
    
    # Print the structured response
    print("\n=== STRUCTURED RESPONSE ===")
    
    if "structured_response" in result:
        response: AgentResponse = result["structured_response"]
        print(f"\n📝 Answer:\n{response.answer}")
        
        if response.sources:
            print(f"\n🔗 Sources ({len(response.sources)}):")
            for i, source in enumerate(response.sources, 1):
                print(f"  {i}. {source.url}")
        else:
            print("\n🔗 Sources: None provided")
    else:
        # Fallback to raw message content if structured response not available
        print("\n(Structured response not available, showing raw output)")
        print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
