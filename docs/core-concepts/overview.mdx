# OmniCoreAgent

The `OmniCoreAgent` class is the primary entry point for the framework. It provides a high-level, user-friendly API for creating and managing AI agents with built-in memory, events, and tool orchestration.

## Initialization

You can initialize an agent with a few lines of code.

```python
from omnicoreagent import OmniCoreAgent

agent = OmniCoreAgent(
    name="my_assistant",
    system_instruction="You are a helpful assistant.",
    model_config={"provider": "openai", "model": "gpt-4o"}
)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Name of the agent (used for session tracking and logging). |
| `system_instruction` | `str` | The high-level objective or persona for the agent. |
| `model_config` | `dict` or `ModelConfig` | Configuration for the LLM provider and model. |
| `mcp_tools` | `list` | (Optional) List of MCP tool configurations. |
| `local_tools` | `ToolRegistry` | (Optional) Custom Python functions registered as tools. |
| `sub_agents` | `list` | (Optional) Specialized agents the parent can delegate to. |
| `agent_config` | `dict` or `AgentConfig` | (Optional) Settings for reasoning steps, timeouts, etc. |
| `memory_router` | `MemoryRouter` | (Optional) Custom memory backend (defaults to in-memory). |
| `event_router` | `EventRouter` | (Optional) Custom event backend (defaults to in-memory). |

---

## Core Methods

### `run()`

Execute a task with the agent. Supports session continuity.

```python
result = await agent.run("What is the weather today?", session_id="user_1")
print(result['response'])
```

- **Query**: The user's input string.
- **Session ID**: (Optional) Provide a unique ID to maintain conversation history.
- **Returns**: A dictionary containing `response`, `session_id`, and `agent_name`.

### `connect_mcp_servers()`

Establishes connections to all configured MCP servers. Call this before `run()` if you are using MCP tools.

```python
await agent.connect_mcp_servers()
```

### `list_all_available_tools()`

Returns a list of all tools currently available to the agent (both MCP and local).

```python
tools = await agent.list_all_available_tools()
```

### `cleanup()`

Cleans up resources, closes MCP connections, and removes temporary configuration files. Always call this when finished.

```python
await agent.cleanup()
```

---

## Session Management

OmniCoreAgent makes it easy to manage conversation history.

### Retrieve History
```python
history = await agent.get_session_history("user_1")
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

### Clear History
```python
# Clear specific session
await agent.clear_session_history("user_1")

# Clear all history for this agent
await agent.clear_session_history()
```

---

## Runtime Switching

You can switch memory and event backends at runtime without restarting the agent.

```python
# Switch to Redis for faster access
await agent.swith_memory_store("redis")

# Switch to MongoDB for document storage
await agent.swith_memory_store("mongodb")

# Switch event store
await agent.switch_event_store("redis_stream")
```

---

## Best Practices

1. **Always Cleanup**: Use `await agent.cleanup()` to avoid orphan processes (especially for MCP).
2. **Session IDs**: Use meaningful session IDs (e.g., user database IDs) to persist context across interactions.
3. **Model Choice**: Use cheaper models (e.g., `gpt-4o-mini`) for simple tasks and powerful ones (e.g., `gpt-4o`) when complex reasoning is required.
