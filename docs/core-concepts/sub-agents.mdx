# Sub-Agents System

Complexity in AI tasks often requires specialization. The **Sub-Agents System** allows you to build a hierarchical architecture where a "Parent" agent can intelligently delegate tasks to specialized "Child" agents.

## Why Use Sub-Agents?

- **Modular Design**: Build and test small, expert agents individually before integrating them.
- **Improved Accuracy**: Specialized agents (e.g., a "Math Expert" or "Code Auditor") are less likely to hallucinate in their specific domain.
- **Tool Management**: Avoid cluttering a single agent's prompt with hundreds of tools. Instead, give each sub-agent only the tools it needs.

---

## Configuration

To use sub-agents, create them individually and then pass them as a list to the parent agent.

```python
from omnicoreagent import OmniCoreAgent

# 1. Create specialized child agents
research_agent = OmniCoreAgent(
    name="researcher",
    system_instruction="You specialize in web research and summarization.",
    ...
)

code_agent = OmniCoreAgent(
    name="coder",
    system_instruction="You are an expert Python developer.",
    ...
)

# 2. Integrate them into the parent agent
parent_agent = OmniCoreAgent(
    name="manager",
    system_instruction="You manage a team of specialists to complete complex requests.",
    sub_agents=[research_agent, code_agent],
    ...
)
```

---

## How Delegation Works

When a parent agent has sub-agents, it is automatically given tools to communicate with them:

| Tool | Action |
|------|--------|
| `call_sub_agent` | Send a specific task to a child agent and wait for the result. |

The parent agent decides *when* a task is too complex or specific and *which* sub-agent is best suited to handle it. The conversation history of the sub-agent is managed independently but can be accessed by the parent.

---

## Example Workflow

1. **User Query**: "Research the latest AI news and write a Python script for a news aggregator."
2. **Manager (Parent)**: Recognizes this requires research and coding.
3. **Manager**: Calls `research_agent` with the task "Get latest AI news summaries".
4. **Researcher (Sub)**: Performs web search, returns summaries.
5. **Manager**: Receives summaries, then calls `code_agent` with "Write a Python aggregator using this data: [summaries]".
6. **Coder (Sub)**: Writes the code, returns it.
7. **Manager**: Synthesizes the final response to the user.

---

## Best Practices

- **Explicit Instructions**: In the parent agent's system instruction, briefly describe the expertise of each sub-agent so it knows who to turn to.
- **Limit Depth**: While hierarchical agents are powerful, avoid nesting agents too deep (e.g., Parent -> Child -> Grandchild) to prevent excessive latency and token usage.
- **Shared Session IDs**: Use the same `session_id` for both parent and child calls if you want them to share context indirectly through the memory store.
