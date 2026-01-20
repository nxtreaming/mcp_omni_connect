# DeepAgent Cookbook

Welcome to the **DeepAgent** learning path. DeepAgent extends OmniCoreAgent with **multi-agent orchestration** — automatically breaking down complex tasks and delegating to specialized subagents running in parallel.

**Follow the examples in order** — each one demonstrates progressively advanced orchestration patterns.

---

## 🎯 What is DeepAgent?

```
DeepAgent = OmniCoreAgent + Multi-Agent Orchestration
```

**Key Insight**: You don't change how DeepAgent works — you change **what domain it operates in** via `system_instruction` and `tools`.

### Architecture Overview

```
User Query
    ↓
Lead Agent (analyzes complexity)
    ↓
Complex task? → YES
    ↓
Spawn Subagents (parallel)
    ├─ Subagent A → Write to /memories/subtask_a/
    ├─ Subagent B → Write to /memories/subtask_b/
    └─ Subagent C → Write to /memories/subtask_c/
    ↓
Lead Agent reads memory → Synthesize → Final Answer
```

**Why Memory-First?**
- Survives context resets
- Enables true parallel execution  
- No context bloat from intermediate results

---

## 📚 The Learning Path

| # | File | Domain | What You'll Learn |
|---|------|--------|-------------------|
| **1** | [basic_usage.py](./basic_usage.py) | **Data Analysis** | Core DeepAgent usage — initialization, task execution, automatic orchestration |
| **2** | [research_analyst.py](./research_analyst.py) | **Research** | Spawning subagents for parallel research tasks |
| **3** | [upwork_proposal_writer.py](./upwork_proposal_writer.py) | **Content Creation** | Complex workflow with 5 specialized tools, multi-step orchestration |
| **4** | [market_research_analyst.py](./market_research_analyst.py) | **Market Research** | Competitor analysis, market sizing, web search integration |
| **5** | [code_review_agent.py](./code_review_agent.py) | **Software Engineering** | Code analysis, security scanning, multi-perspective review |
| **6** | [code_architect.py](./code_architect.py) | **Architecture** | System design patterns, scalability analysis |
| **7** | [vula_due_diligence/](./vula_due_diligence/) | **Investment Analysis** | **Production System**: Full due diligence with HTML reports, infographics, batch processing |

---

## 🎯 "I just want to..."

| Goal | Example |
|------|---------|
| Understand the basics | [basic_usage.py](./basic_usage.py) |
| Build a research agent | [research_analyst.py](./research_analyst.py) |
| Create a content writer | [upwork_proposal_writer.py](./upwork_proposal_writer.py) |
| Analyze competitors | [market_research_analyst.py](./market_research_analyst.py) |
| Review code automatically | [code_review_agent.py](./code_review_agent.py) |
| Build a production system | [vula_due_diligence/](./vula_due_diligence/) |

---

## 🛠️ Prerequisites

```bash
# Required
pip install omnicoreagent

# Create .env file
LLM_API_KEY=your_key_here
LLM_PROVIDER=openai  # or anthropic, google, etc.
LLM_MODEL=gpt-4o

# Optional (for advanced examples)
TAVILY_API_KEY=your_tavily_key  # For web search (market research, due diligence)
```

---

## 📖 Example Breakdown

### 1. basic_usage.py — Your First DeepAgent

**What it demonstrates:**
- Minimal DeepAgent setup (~20 lines)
- Automatic orchestration based on task complexity
- Memory-first architecture

**Key Code:**
```python
agent = DeepAgent(
    name="DataAnalyst",
    system_instruction="You are a senior data analyst.",
    model_config={"provider": "openai", "model": "gpt-4o"},
)

await agent.initialize()
result = await agent.run("Analyze key factors affecting sales...")
```

**When the agent decides to orchestrate:**
- Simple query → Direct answer
- Complex query → Spawns subagents automatically

---

### 2. research_analyst.py — Parallel Research

**What it demonstrates:**
- Spawning multiple research subagents in parallel
- Each subagent focuses on one research angle
- Memory aggregation for synthesis

**Use case:** "Research AI applications in healthcare" spawns:
- Medical AI researcher
- Regulatory compliance analyst  
- Market adoption analyst

---

### 3. upwork_proposal_writer.py — Custom Tools + Orchestration

**What it demonstrates:**
- 5 specialized tools for proposal writing
- Multi-step workflow (research → analyze → write)
- Domain-specific orchestration

**Tools included:**
- `search_upwork_jobs`
- `get_client_profile`
- `analyze_job_requirements`
- `generate_proposal_outline`
- `write_proposal_section`

**Workflow:**
```
User: "Write proposal for Python automation job"
    ↓
Agent spawns:
├─ Job Requirements Analyst
├─ Client Research Specialist
└─ Proposal Writer
    ↓
Synthesizes into polished proposal
```

---

### 4. market_research_analyst.py — Web Search Integration

**What it demonstrates:**
- Tavily API integration for real-time web search
- Competitor landscape analysis
- Market sizing with live data

**Requires:** `TAVILY_API_KEY` in `.env`

**Example task:** "Analyze the electric vehicle market in Europe"

**Agent spawns:**
- Market size researcher (web search for TAM/SAM)
- Competitor analyst (Tesla, VW, BYD comparisons)
- Trend forecaster (growth projections)

---

### 5. code_review_agent.py — Software Analysis

**What it demonstrates:**
- Static code analysis
- Security vulnerability scanning
- Multi-perspective code review

**Tools included:**
- `read_codebase`
- `run_static_analysis`
- `check_security_vulnerabilities`
- `suggest_improvements`

**Agent spawns:**
- Security reviewer
- Performance analyst
- Code quality checker

---

### 6. code_architect.py — System Design

**What it demonstrates:**
- Architecture pattern recognition
- Scalability analysis
- Design trade-off evaluation

**Use case:** "Review microservices architecture for e-commerce platform"

---

### 7. vula_due_diligence/ — Production System

**This is the crown jewel** — a complete production system for investment due diligence.

**What it includes:**
- **TUI Interface** - Interactive terminal UI for live monitoring
- **Batch Processing** - Evaluate multiple companies concurrently
- **Report Generation** - HTML reports with professional styling
- **Infographics** - Goldman Sachs-style investment dashboards
- **Web Search** - Real-time research via Tavily API
- **Memory Persistence** - All findings saved to local memory

**Files:**
```
vula_due_diligence/
├── main.py                 # Entry point (TUI or CLI mode)
├── engine/
│   ├── deep_agent_runner.py   # Core DeepAgent workflow
│   ├── batch_processor.py     # Concurrent evaluation
│   └── vula_tools.py          # Report generation tools
├── tui/
│   └── app.py                 # Textual-based TUI
└── README.md                  # Full documentation
```

**Run it:**
```bash
# Interactive TUI mode
python cookbook/deep_agent/vula_due_diligence/main.py

# CLI mode - single company
python cookbook/deep_agent/vula_due_diligence/main.py --company "Stripe"

# Batch mode - multiple companies
python cookbook/deep_agent/vula_due_diligence/main.py --batch companies.csv --parallel 3
```

---

## 📖 Key Concepts

### Automatic Orchestration

DeepAgent doesn't require you to manually configure when to spawn subagents. It decides based on:

| Task Complexity | Behavior |
|----------------|----------|
| **Simple** | Direct answer (no orchestration) |
| **Medium** | 1-2 focused subagents |
| **Complex** | Multiple parallel subagents |

### Memory-First Workflow

Traditional approach (context-based):
```
Subagent A → Returns 5000 tokens
Subagent B → Returns 6000 tokens
Subagent C → Returns 4000 tokens
Total: 15,000 tokens in context ❌
```

DeepAgent approach (memory-based):
```
Subagent A → Writes to /memories/subtask_a/
Subagent B → Writes to /memories/subtask_b/
Subagent C → Writes to /memories/subtask_c/
Lead reads memory when needed ✅
Context stays lean
```

### Configuration Best Practices

DeepAgent uses **smart defaults** optimized for orchestration:

```python
agent_config = {
    "max_steps": 50,  # More steps for coordination
    "tool_call_timeout": 600,  # 10 min (subagents do deep work)
    "memory_tool_backend": "local",  # ENFORCED (cannot override)
    "context_management": {"enabled": True},
    "tool_offload": {"enabled": True},
}
```

**Key notes:**
- `memory_tool_backend` is always `"local"` (required for orchestration)
- You can override most settings, but memory backend is non-negotiable

---

## 🎓 Design Patterns

### Pattern 1: Research & Synthesis

```python
agent = DeepAgent(
    name="Researcher",
    system_instruction="You are a research coordinator.",
    model_config={...},
)

# Agent automatically:
# 1. Spawns parallel researchers
# 2. Each writes findings to memory
# 3. Synthesizes comprehensive report
```

### Pattern 2: Domain Expert + Custom Tools

```python
tools = ToolRegistry()

@tools.register_tool("domain_tool")
def my_tool(params):
    return results

agent = DeepAgent(
    name="Expert",
    system_instruction="You are a domain expert...",
    local_tools=tools,  # Your tools + orchestration tools
)
```

### Pattern 3: Batch Processing

For evaluating multiple items:

```python
# See vula_due_diligence/engine/batch_processor.py
processor = BatchProcessor(...)
results = await processor.process_batch(companies, max_concurrent=3)
```

---

## 🚀 Running the Examples

```bash
# Basic usage
python cookbook/deep_agent/basic_usage.py

# Research analyst
python cookbook/deep_agent/research_analyst.py

# Upwork proposal writer
python cookbook/deep_agent/upwork_proposal_writer.py

# Market research (requires TAVILY_API_KEY)
python cookbook/deep_agent/market_research_analyst.py

# Code review
python cookbook/deep_agent/code_review_agent.py

# Production system (TUI mode)
python cookbook/deep_agent/vula_due_diligence/main.py
```

---

## 🆚 DeepAgent vs OmniCoreAgent

| Feature | OmniCoreAgent | DeepAgent |
|---------|---------------|-----------|
| **Domain** | User-defined | User-defined (same) |
| **Tools** | User-provided | User-provided + orchestration |
| **Memory** | Optional | Always `"local"` (enforced) |
| **Orchestration** | No | Automatic subagent spawning |
| **Complexity** | Single-agent workflows | Multi-agent coordination |
| **Best For** | Most use cases | Complex analysis, research, multi-perspective tasks |

**When to use DeepAgent:**
✅ Multi-domain research (tech + market + legal)
✅ Parallel analysis (compare multiple options)
✅ Complex synthesis (aggregate findings from multiple sources)
✅ Long-running investigations

**When to use OmniCoreAgent:**
✅ Simple Q&A
✅ Single-perspective tasks
✅ Direct tool execution
✅ Chat interfaces

---

## 💡 Tips for Success

1. **Clear System Instructions**: Define the domain expertise clearly
2. **Task Complexity**: DeepAgent shines on tasks that benefit from parallel work
3. **Memory Organization**: Use descriptive paths like `/memories/project_name/subtask/`
4. **Trust the LLM**: Let the agent decide when to orchestrate
5. **Increase max_steps**: If orchestration is failing, try `max_steps=75` or `max_steps=100`

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not spawning subagents | Task may be too simple, or increase `max_steps` |
| Memory not persisting | Ensure `memory_tool_backend: "local"` (should be automatic) |
| Subagents timing out | Increase `tool_call_timeout` in `agent_config` |
| Context overflow | Enable `tool_offload` and `context_management` |

---

## 📚 Further Reading

- **[DeepAgent Documentation](../../docs/deep-agent.md)** - Full API reference, architecture diagrams
- **[Main README](../../README.md#6--deepagent-multi-agent-orchestration)** - Overview and comparison
- **[Getting Started](../getting_started/)** - Learn OmniCoreAgent fundamentals first

---

## 🚀 Next Steps

After mastering DeepAgent:
- **[Workflows](../workflows/)** - Combine multiple agents with Sequential/Parallel/Router patterns
- **[Background Agents](../background_agents/)** - Schedule autonomous tasks
- **[Production](../production/)** - Deploy with monitoring and observability
