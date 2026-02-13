# Workflow Agents

For tasks that require more than one agent working in concert, OmniCoreAgent provides high-level **Workflow Agents**. These allow you to orchestrate multiple agents in sequential, parallel, or routed patterns.

---

## 🚀 SequentialAgent

The `SequentialAgent` runs a list of sub-agents one after another. The output of the previous agent becomes the input (or context) for the next one.

**Best for**: Clear, linear processes like "Analyze data -> Write report -> Proofread report".

```python
from omnicoreagent import SequentialAgent

seq_agent = SequentialAgent(
    sub_agents=[analyzer_agent, writer_agent, editor_agent]
)

result = await seq_agent.run(initial_task="Analyze these sales numbers and write a summary.")
```

---

## ⚡ ParallelAgent

The `ParallelAgent` runs multiple agents simultaneously. Each agent handles a specific assigned task, and the results are returned as a consolidated dictionary.

**Best for**: Speeding up independent tasks, like fetching data from three different sources at once.

```python
from omnicoreagent import ParallelAgent

par_agent = ParallelAgent(
    sub_agents=[agent_a, agent_b, agent_c]
)

results = await par_agent.run(
    agent_tasks={
        "agent_a": "Get user profile",
        "agent_b": "Get order history",
        "agent_c": "Get recommendation status"
    }
)
```

---

## 🚦 RouterAgent

The `RouterAgent` uses an LLM to look at a user query and determine which sub-agent is best suited to handle it. It effectively acts as an intelligent dispatcher.

**Best for**: Centralized help desks or complex systems with many specialists.

```python
from omnicoreagent import RouterAgent

router = RouterAgent(
    sub_agents=[billing_agent, technical_agent, sales_agent],
    model_config={"provider": "openai", "model": "gpt-4o"}
)

# If the query is about an invoice, it routes to billing_agent automatically.
result = await router.run(task="Why was I charged twice last month?")
```

---

## Comparison Table

| Workflow Type | Execution | Dependencies | Use Case |
|---------------|-----------|--------------|----------|
| **Sequential** | Serial | One-way (A -> B -> C) | Multi-stage manufacturing or editing. |
| **Parallel** | Concurrent | None (Independent) | Batch processing and fast data retrieval. |
| **Router** | Conditional | None (LLM decided) | Specialized support bots or tool gateways. |

---

## Best Practices

1. **Context Management**: In a `SequentialAgent`, ensure each agent returns clear, concise information so the next agent has enough context to proceed without hitting token limits.
2. **Error Isolation**: In a `ParallelAgent`, if one sub-agent fails, the framework will return the partial results plus the error. Check for these errors in your result dictionary.
3. **Routing Instructions**: For `RouterAgent`, give your sub-agents very clear names and single-sentence descriptions so the LLM knows exactly when to use each one.
