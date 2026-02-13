# Observability & Tracing

Ensuring your agents are performing correctly requires visibility into their reasoning cycles, tool calls, and model outputs. OmniCoreAgent integrates with **Opik** to provide production-grade tracing and observability.

---

## Opik Tracing

Opik allows you to visualize the nested structure of your agent's reasoning. You can see exactly what query was sent, what tools were called (including their inputs and outputs), and the final response.

### Configuration

Enable Opik tracing by setting the following environment variables:

```bash
OPIK_API_KEY=your_opik_api_key
OPIK_PROJECT_NAME=my_agent_project
```

The framework will automatically detect these variables and start sending traces to your Opik dashboard.

---

## Debug Mode

For local development and troubleshooting, you can enable verbose logging.

```python
agent = OmniCoreAgent(
    ...
    debug=True  # Enables detailed console logging
)
```

In debug mode, you will see:
- Full system prompts being sent.
- Raw LLM responses.
- Detailed connection status for each MCP server.
- Execution times for local tools.

---

## Token & Request Tracking

OmniCoreAgent provides built-in mechanisms to track and limit resource usage to prevent unexpected costs.

### Setting Limits
```python
agent_config = {
    "request_limit": 100,      # Max 100 LLM calls per session
    "total_tokens_limit": 500000 # Stop if session hits 500k tokens
}
```

---

## Performance Monitoring

Through the [Event System](../core-features/event-system.md), you can calculate performance metrics:

- **Latency**: Measure the time between `user_message` and `final_answer`.
- **Tool Efficiency**: Track how many tool calls are made per query.
- **Error Rates**: Monitor `BACKGROUND_TASK_ERROR` events in background agents to identify unstable MCP servers.

---

## Best Practices

- **Project Isolation**: Use different `OPIK_PROJECT_NAME` values for development, staging, and production environments.
- **Sensitive Data**: Be careful when tracing agents that handle PII. Opik traces include full message contents by default.
- **Monitoring Events**: In production, pipe your [real-time events](../core-features/event-system.md) into ELK, Datadog, or Sentry for long-term alerting.
