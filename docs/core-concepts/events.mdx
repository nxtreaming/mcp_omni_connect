# Event System

OmniCoreAgent provides a powerful, real-time event system that allows you to monitor agent progress, tool execution, and communication flows.

## Core Concepts

The event system uses an **EventRouter** to handle events internally. Like memory, you can switch between different event stores.

| Backend | Identifier | Description |
|---------|------------|-------------|
| **In-Memory** | `in_memory` | Simple event storage for development. |
| **Redis Stream** | `redis_stream` | Persistent, scalable event streaming for production. |

---

## Event Types

The framework emits various event types that you can listen for:

| Event Type | Description |
|------------|-------------|
| `user_message` | When the agent receives a query. |
| `agent_message` | When the agent sends a plain response. |
| `agent_thought` | Internal reasoning steps (Chain of Thought). |
| `tool_call_started` | When the agent begins executing a tool. |
| `tool_call_result` | When a tool returns its output. |
| `final_answer` | The terminal response to the user. |
| `sub_agent_started` | When a child agent is invoked. |
| `sub_agent_result` | When a child agent completes its task. |

---

## Streaming Events

You can loop over events in real-time as the agent works.

```python
async for event in agent.stream_events(session_id="user_1"):
    print(f"[{event.type}] -> {event.payload}")
```

### Manual Retrieval

You can also fetch the entire event history for a session:

```python
events = await agent.get_events(session_id="user_1")
for event in events:
    print(event)
```

---

## Runtime Switching

Switch between event stores on the fly.

```python
# Switch to Redis Streams for manufacturing-grade durability
await agent.switch_event_store("redis_stream")

# Check current store type
store_type = await agent.get_event_store_type()
```

---

## Use Cases

1. **Real-time UIs**: Stream agent "thoughts" and tool calls to a frontend to keep users informed.
2. **Auditing**: Persist all agent actions to a database or log file for later review.
3. **Internal Monitoring**: Trigger alerts if certain tool calls fail or if the agent enters a loop.
4. **Debugging**: Use `in_memory` events during development to trace exactly why an agent took a certain path.
