# Quick Start

Get your first AI agent running in under 30 seconds with OmniCoreAgent.

## 1. Set API Key

Create a `.env` file in your project directory:

```bash
echo "LLM_API_KEY=your_openai_api_key_here" > .env
```

!!! tip "Supported Providers"
    You can use keys from OpenAI, Anthropic, Google Gemini, Groq, DeepSeek, and more.

## 2. Create Your First Agent

Create a file named `hello_agent.py`:

```python
import asyncio
from omnicoreagent import OmniCoreAgent

async def main():
    # 1. Initialize the agent
    agent = OmniCoreAgent(
        name="my_agent",
        system_instruction="You are a helpful assistant.",
        model_config={"provider": "openai", "model": "gpt-4o"}
    )
    
    # 2. Run a task
    result = await agent.run("Hello, what can you do?")
    print(f"Agent Response: {result['response']}")
    
    # 3. Cleanup
    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Run It

```bash
python hello_agent.py
```

**✅ That's it!** You just built an AI agent with session management, memory persistence, and error handling.

---

## 🚀 Adding Tools (MCP)

OmniCoreAgent can connect to any MCP-compatible service. Here's how to add a filesystem tool:

```python
agent = OmniCoreAgent(
    name="fs_agent",
    system_instruction="You can manage files.",
    model_config={"provider": "openai", "model": "gpt-4o"},
    mcp_tools=[
        {
            "name": "filesystem",
            "transport_type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        }
    ]
)

await agent.connect_mcp_servers()
result = await agent.run("List files in /tmp")
```

---

## 🧠 Persistence with Session IDs

Agents remember context when you provide a `session_id`:

```python
# Session 1
result1 = await agent.run("My name is Abiola.", session_id="user_123")

# Session 2 (Agent remembers the name)
result2 = await agent.run("What is my name?", session_id="user_123")
```

---

## Next Steps

Now that you've seen the basics:

1. **[Explore Core Features](../core-features/omnicoreagent.md)** - Deep dive into memory and events.
2. **[Learn about Agent Types](../agent-types/sub-agents.md)** - Build workflows and background agents.
3. **[Advanced Tool Use](../advanced/advanced-tool-use.md)** - Scale to 1000+ tools with BM25.
