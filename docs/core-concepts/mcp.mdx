# MCP Client Integration

OmniCoreAgent features a robust, built-in client for the **Model Context Protocol (MCP)**. It allows your agents to connect to any MCP-compliant server to access tools, resources, and context.

## Configuration

MCP servers are configured via the `mcp_tools` parameter during agent initialization.

```python
agent = OmniCoreAgent(
    ...
    mcp_tools=[
        {
            "name": "my_server",
            "transport_type": "stdio",
            "command": "npx",
            "args": ["-y", "@user/mcp-server-example"]
        }
    ]
)
```

---

## Transport Types

OmniCoreAgent supports three primary transport methods:

### 1. `stdio` (Local)
Used for local MCP servers running as separate processes. This is the most common for CLI-based servers.

```python
{
    "name": "filesystem",
    "transport_type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home"]
}
```

### 2. `streamable_http` (Remote)
Used for remote servers communicating over HTTP. Supports full streaming and complex authentication.

```python
{
    "name": "github",
    "transport_type": "streamable_http",
    "url": "http://api.myserver.com/mcp",
    "headers": {"Authorization": "Bearer key"}
}
```

### 3. `sse` (Real-time)
Used for Server-Sent Events transports, typically for real-time data streaming.

```python
{
    "name": "live_data",
    "transport_type": "sse",
    "url": "http://localhost:3000/sse"
}
```

---

## Authentication

The built-in client supports production-grade authentication methods.

### Bearer Token
Simple header-based authentication.

```python
{
    "name": "private_api",
    "transport_type": "streamable_http",
    "headers": {
        "Authorization": "Bearer your_secret_token"
    }
}
```

### OAuth 2.0
Supports full OAuth 2.0 flows. When initialized, the agent will handle the token exchange.

```python
{
    "name": "oauth_server",
    "transport_type": "streamable_http",
    "auth": {
        "method": "oauth"
    },
    "url": "http://localhost:8000/mcp"
}
```

---

## Managing Connections

### Connecting
Always remember to connect to your servers before running tasks.

```python
await agent.connect_mcp_servers()
```

### Listing Tools
Verify your connections by listing available tools.

```python
tools = await agent.list_all_available_tools()
```

### Cleanup
Properly close all MCP connections when the agent is no longer needed.

```python
await agent.cleanup()
```

---

## Technical Details

| Feature | Description |
|---------|-------------|
| **Isolation** | Each MCP server runs in its own connection context. |
| **Timeout** | Configurable via `tool_call_timeout` in agent settings. |
| **Discovery** | Tools are automatically discovered and converted to agent-ready formats. |
| **Retries** | Built-in retry logic for transient connection failures. |
