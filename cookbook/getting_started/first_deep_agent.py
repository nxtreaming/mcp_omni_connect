#!/usr/bin/env python3
"""
First DeepAgent Example

Create a minimal DeepAgent with multi-agent orchestration.
This example shows how to delegate tasks to specialized subagents.

Run:
    python cookbook/getting_started/first_deep_agent.py
"""

import asyncio

from omnicoreagent import DeepAgent


async def main():
    # Create a DeepAgent with orchestration capabilities
    agent = DeepAgent(
        name="research_coordinator",
        system_instruction="""
You are a research coordinator. Break down complex research tasks
into focused subtasks and delegate them to specialized subagents.
        """,
        model_config={"provider": "openai", "model": "gpt-4o"},
    )

    #  Initialize the agent (sets up subagent spawning tools)
    await agent.initialize()

    # Run a complex query that will spawn subagents
    query = """
Research the benefits of serverless computing for AI applications.
Create one subagent to research cost benefits and another for scalability.
    """
    
    result = await agent.run(query)
    print(f"Response: {result['response']}")
    print(f"Session ID: {result['session_id']}")
    print(f"Metrics: {result['metric']}")

    # Clean up resources
    await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
