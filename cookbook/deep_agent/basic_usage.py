"""
Basic DeepAgent Usage.

DeepAgent = OmniCoreAgent + Multi-Agent Orchestration
Works for any domain based on your system_instruction and tools.

Run: python cookbook/deep_agent/basic_usage.py
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from omnicoreagent import DeepAgent


async def main():
    """Basic DeepAgent example - works for any domain."""
    
    # Your system_instruction defines the domain
    agent = DeepAgent(
        name="DataAnalyst",
        system_instruction="""
You are a senior data analyst.
You excel at breaking down complex analysis tasks and producing insights.
""",
        model_config={
            "provider": os.getenv("LLM_PROVIDER", "openai"),
            "model": os.getenv("LLM_MODEL", "gpt-4o"),
        },
    )
    
    await agent.initialize()
    print(f"✓ Initialized: {agent.name}")
    print(f"✓ Task ID: {agent.task_id}")
    
    # For complex tasks, agent can spawn subagents automatically
    print("\n🚀 Running agent...")
    result = await agent.run("""
    Analyze the key factors affecting sales performance.
    Consider: seasonal trends, regional differences, product categories.
    """)
    
    print(f"\n📋 Result:\n{result['response'][:800]}...")
    
    await agent.cleanup()
    print("\n✓ Done")


if __name__ == "__main__":
    asyncio.run(main())
