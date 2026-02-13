# Memory System

OmniCoreAgent features a flexible, multi-tier memory system that allows you to store and retrieve conversation history across different storage backends.

## Supported Backends

| Backend | Identifier | Description | Required Config |
|---------|------------|-------------|-----------------|
| **In-Memory** | `in_memory` | Fast, transient storage for development and testing. | None |
| **Redis** | `redis` | High-performance persistence for production. | `REDIS_URL` |
| **Database** | `database` | SQL persistence (PostgreSQL, MySQL, SQLite). | `DATABASE_URL` |
| **MongoDB** | `mongodb` | Document-based persistence for complex JSON. | `MONGODB_URI` |
| **File-Based** | `local` | Simple local file storage (via Memory Tool Backend). | None |

---

## Configuration

To use a specific memory backend, you can pass a `MemoryRouter` during initialization or set environment variables.

### Environment Variables

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# SQL Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# MongoDB
MONGODB_URI=mongodb://localhost:27017/omnicoreagent
```

### Manual Initialization

```python
from omnicoreagent import OmniCoreAgent, MemoryRouter

# Use Redis explicitly
agent = OmniCoreAgent(
    ...
    memory_router=MemoryRouter("redis")
)
```

---

## Runtime Switching

One of the most powerful features of OmniCoreAgent is the ability to switch memory stores at runtime. This is useful for migrating data or switching between fast cache and long-term storage.

```python
# Start with in-memory for speed
agent = OmniCoreAgent(name="my_agent", ...)

# Switch to persistent database when needed
await agent.swith_memory_store("database")

# Switch back to Redis for low-latency tasks
await agent.swith_memory_store("redis")
```

---

## Memory Management

The agent automatically handles message storage during `run()`. You can also manually interact with the history.

### Retrieve History
```python
messages = await agent.get_session_history(session_id="user_1")
```

### Clear History
```python
# Clear a specific session
await agent.clear_session_history(session_id="user_1")

# Reset all memory for this agent
await agent.clear_session_history()
```

---

## Memory Architectures

### Sliding Window
By default, the agent uses a sliding window to manage context window limits. You can configure this in `agent_config`.

```python
agent_config = {
    "memory_config": {
        "mode": "sliding_window", 
        "value": 10000 # Keep last 10k tokens
    }
}
```

### Token Budget
Manage history based on a strict token budget.

```python
agent_config = {
    "memory_config": {
        "mode": "token_budget", 
        "value": 30000 # Strict 30k token limit
    }
}
```

---

> [!TIP]
> For production deployments, we recommend using **Redis** for session cache and **PostgreSQL/MongoDB** for long-term archival.
