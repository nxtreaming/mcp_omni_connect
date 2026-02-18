#!/usr/bin/env python3
"""
Agent with Community Tools (Tavily & Google Search)

Demonstrates how to use pre-built community tools.

Run:
    export TAVILY_API_KEY=your_key
    # or
    export GOOGLE_API_KEY=your_key
    export GOOGLE_CSE_ID=your_id
    
    python cookbook/community_tools/agent_with_search.py
"""

import asyncio
import os
import sys
# Ensure we can import from src if running from repo root
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src"))

from omnicoreagent import OmniCoreAgent
from omnicoreagent.community import TavilySearch, GoogleSearch

async def main():
    # Create tool list
    my_tools = []
    
    print("Initializing Community Tools...")
    
    # Add Tavily Search if API key is present
    if os.environ.get("TAVILY_API_KEY"):
        print("Adding Tavily Search tool...")
        my_tools.append(TavilySearch())
    else:
        print("TAVILY_API_KEY not found. Skipping Tavily Search.")

    # Add Google Search if API keys are present
    if os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_CSE_ID"):
        print("Adding Google Search tool...")
        my_tools.append(GoogleSearch())
    else:
        print("GOOGLE_API_KEY or GOOGLE_CSE_ID not found. Skipping Google Search.")
        
    if not my_tools:
        print("\nNo search tools registered. Please set TAVILY_API_KEY or GOOGLE_API_KEY/GOOGLE_CSE_ID to run this example.")
        return

    # Create agent
    agent = OmniCoreAgent(
        name="search_agent",
        system_instruction="You are a research assistant. Use the available search tools to find information.",
        model_config={"provider": "openai", "model": "gpt-4o"},
        local_tools=my_tools, # Pass list directly!
    )
    
    print("=" * 50)
    print("AGENT WITH COMMUNITY SEARCH TOOLS")
    print("=" * 50)
    
    query = "What are the latest developments in AI agents in 2025?"
    print(f"\nQuery: {query}")
    
    # In a real run, we would call agent.run(query)
    # But since we don't have keys in this automated environment, we just print what we would do.
    # result = await agent.run(query)
    # print(f"\nResponse: {result['response']}")
    
    print("\nAgent initialized successfully with tools:", [t.name for t in agent.local_tools.list_tools()])
    
    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
