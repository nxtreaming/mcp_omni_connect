from omnicoreagent import OmniCoreAgent
from omnicoreagent.core.tools.local_tools_registry import ToolRegistry, Tool
from omnicoreagent.community import TavilySearch, LocalPython
import os

# 1. Define your CUSTOM tool (Standard Way)
class MyCustomTool:
    def get_tool(self) -> Tool:
        return Tool(
            name="greet_user",
            description="Greets the user by name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
            function=self._greet
        )
    
    def _greet(self, name: str):
        return {"status": "success", "data": f"Hello, {name}!", "message": "Greeting sent"}

# 2. Create the Registry (Manually)
registry = ToolRegistry()

# 3. Register your CUSTOM tool
custom_tool = MyCustomTool()
registry.register(custom_tool)

# 4. Register PREBUILT community tools (They work the exact same way!)
# Just instantiate safely and register them.
tavily_tool = TavilySearch(api_key=os.getenv("TAVILY_API_KEY"))
registry.register(tavily_tool)

python_tool = LocalPython()
registry.register(python_tool)

# 5. Pass the MIXED registry to the agent
agent = OmniCoreAgent(
    name="HybridAgent",
    system_instruction="You have search, python, and a custom greeter.",
    model_config={"provider": "gemini", "model": "gemini-1.5-flash"},
    local_tools=registry,  # <--- Passing the Registry directly (Option B)
)

# Now the agent has access to ALL 3 tools.
print("Registered Tools:", registry.list_tools())
