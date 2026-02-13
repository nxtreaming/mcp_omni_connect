# Advanced Tool Use (BM25)

As you scale your AI systems, you may find that your agent has access to hundreds or even thousands of tools across multiple MCP servers. Passing all tool schemas to the LLM in every request is expensive and exceeds context window limits.

**Advanced Tool Use** solves this by dynamically discovering the most relevant tools for each task at runtime using lexical search.

---

## How It Works

OmniCoreAgent uses the **BM25 algorithm** (a state-of-the-art lexical search method) to filter your tool registry.

1. **Indexing**: When the agent starts, it indexes the names, descriptions, and parameters of all registered tools (Local and MCP).
2. **Retrieval**: When you call `agent.run(query)`, the agent uses your query as a search term.
3. **Injection**: It retrieves the top 5 (default) most relevant tools and injects only their schemas into the current reasoning cycle.
4. **Deterministic**: This process is entirely local and requires no external network calls or vector databases.

---

## Configuration

Enable advanced tool use in the agent configuration:

```python
agent_config = {
    "enable_advanced_tool_use": True  # Enable BM25 retrieval
}

agent = OmniCoreAgent(
    ...
    agent_config=agent_config
)
```

---

## Benefits

| Benefit | Description |
|---------|-------------|
| **Scalability** | Support 1000+ tools without hitting context limits. |
| **Token Savings** | Save thousands of tokens per request by only sending relevant schemas. |
| **Speed** | Lexical search is incredibly fast (sub-millisecond) and runs entirely in memory. |
| **Deterministic** | BM25 is a keyword-based algorithm, making retrieval outcomes predictable and easy to debug. |

---

## Best Practices

- **Descriptive Names**: Ensure your MCP tool names and local function names are descriptive (e.g., `fetch_user_email` instead of `cmd1`).
- **Rich Descriptions**: The more detail you provide in your docstrings and MCP descriptions, the more accurate the BM25 retrieval will be.
- **Query Clarity**: The agent's search is only as good as the user's query. If the query is vague, the agent may not find the right tool.

---

> [!NOTE]
> Advanced Tool Use is highly recommended for production systems where agents interact with multiple MCP servers or extensive local libraries.
