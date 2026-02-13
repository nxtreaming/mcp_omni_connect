# Background Agent System

The **Background Agent System** provides a framework for creating autonomous agents that execute tasks on a schedule. These agents are ideal for system monitoring, periodic reports, and data synchronization.

## BackgroundAgentService

The `BackgroundAgentService` is the primary manager for background agents. It handles scheduling, status tracking, and resource management.

```python
from omnicoreagent import BackgroundAgentService, MemoryRouter, EventRouter

# 1. Initialize the service with routers
bg_service = BackgroundAgentService(
    MemoryRouter("redis"),
    EventRouter("redis_stream")
)

# 2. Start the manager
bg_service.start_manager()
```

---

## Creating a Background Agent

To create a background agent, define its configuration including the `interval` (in seconds) and the `query` it should run.

```python
agent_config = {
    "agent_id": "system_monitor",
    "system_instruction": "Monitor system resources and alert if usage is high.",
    "model_config": {"provider": "openai", "model": "gpt-4o-mini"},
    "interval": 300,  # Run every 5 minutes
    "task_config": {
        "query": "Check local CPU and Memory usage.",
        "max_retries": 2
    }
}

# Create and register the agent
await bg_service.create(agent_config)

# Start the agent
bg_service.start_agent("system_monitor")
```

---

## Management API

The service provides a comprehensive API to manage your background fleet:

| Method | Description |
|--------|-------------|
| `start_agent(agent_id)` | Begin the scheduled execution for an agent. |
| `pause_agent(agent_id)` | Temporarily stop the agent's schedule. |
| `resume_agent(agent_id)` | Resume a paused agent. |
| `stop_agent(agent_id)` | Completely stop and remove the agent from the schedule. |
| `get_agent_status(agent_id)` | Get detailed metrics (run count, error count, last run time). |
| `list_agents()` | List all managed background agents. |

---

## Observability

Background agents emit events just like standard agents. You can stream these events to monitor "self-flying" tasks in real-time.

```python
# Stream events for a background agent
async for event in bg_service.stream_agent_events("system_monitor"):
    print(f"[{event.type}] {event.payload}")
```

### Event Types
- `background_task_started`
- `background_task_completed`
- `background_task_error`
- `background_agent_status`

---

## Use Cases

### 1. 🗄️ Database Archival
Run an agent every 24 hours to find old records and archive them to S3 or a secondary database.

### 2. 🚨 Sytem Health Checks
Monitor disk space, memory usage, and service availability every 60 seconds.

### 3. 📰 Content Aggregator
An agent that fetches news from several sources once an hour, summarizes them, and saves the result to your blog or newsletter database.

---

## Best Practices

- **Timeout Management**: Ensure your `tool_call_timeout` and `interval` are balanced. If a task takes 10 minutes but the interval is 5 minutes, you may experience overlaps.
- **Resource Limits**: Set `request_limit` and `total_tokens_limit` in the agent config to prevent runaway costs if an agent gets stuck in a loop.
- **Persistent Storage**: Always use `redis` or `database` memory and event stores for background agents to ensure you don't lose progress if your main process restarts.