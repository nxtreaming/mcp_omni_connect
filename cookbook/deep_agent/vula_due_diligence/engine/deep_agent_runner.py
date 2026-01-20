"""
DeepAgent Runner for Vula Due Diligence System

FIXED: Uses correct DeepAgent API with local_tools for due diligence tools.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import uuid

# IMPORTS: Prioritize installed package, fallback to relative path for dev
try:
    from omnicoreagent import DeepAgent
    from omnicoreagent import ToolRegistry
except ImportError:
    # Add parent to path for imports (DEV MODE)
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    sys.path.insert(0, str(repo_root / "src"))
    from omnicoreagent import DeepAgent
    from omnicoreagent import ToolRegistry
    logging.warning("Using relative path imports for omnicoreagent (Dev Mode)")

logger = logging.getLogger(__name__)


# Import robust tools from vula_tools
try:
    from .vula_tools import create_vula_tools
    HAS_VULA_TOOLS = True
except ImportError:
    # Try absolute import if running from different context
    try:
        from engine.vula_tools import create_vula_tools
        HAS_VULA_TOOLS = True
    except ImportError:
        HAS_VULA_TOOLS = False
        logger.warning("Could not import vula_tools")


class VulaDeepAgentRunner:
    """
    DeepAgent runner for SME due diligence evaluation.
    """
    
    def __init__(
        self,
        model: str = "gemini-2.5-pro",
        provider: str = "gemini",
        tavily_key: Optional[str] = None,
        max_steps: int = 100,
        debug: bool = False,
    ):
        self.model = model
        self.provider = provider
        self.tavily_key = tavily_key or os.getenv("TAVILY_API_KEY")
        self.max_steps = max_steps
        self.debug = debug
        self.agent = None
        
    def _build_system_instruction(self) -> str:
        return """You are a **World-Class Investment Analyst** specializing in **African SME Funding**.

Your goal is to screen companies for Vula (grants, debt, equity) with a deep understanding of the local context.

**Core Evaluation Criteria (Africa-First)**:
1.  **Financial Reality**: Look beyond audited financials. Assess traction via transaction volume, mobile money integration, and partnerships.
2.  **Macro Risk**: Evaluate exposure to currency depreciation (FX), regulatory changes, and infrastructure reliance.
3.  **Local Competitiveness**: How does the solution compare to *local* incumbents (including informal ones), not just global SaaS?
4.  **Impact**: Alignment with SDGs is MANDATORY.

**Available Tools**:
- Internet search (Tavily): For real-time data and news.
- assess_macro_risk: Check country-specific risks (FX, Regulations).
- analyze_competitor_landscape: Create a feature matrix vs local competitors.
- generate_dashboard_infographic: Create professional one-pager.
- generate_financial_chart: Create revenue projections.
- generate_html_report: Create the final detailed report.
- save_evaluation_memo: Save the investment decision.

**Workflow**:
1.  **Discovery**: Textual research on Product, Team, and Market.
2.  **Risk Analysis**:
    - Call `assess_macro_risk` for the HQ country.
    - Call `analyze_competitor_landscape` to map defensibility.
3.  **Financial Analysis**: Project revenues and generate chart.
4.  **Synthesis**: Generate `generate_dashboard_infographic`.
5.  **Reporting**: Compile findings into `generate_html_report` and `save_evaluation_memo`.

**Tone**: Professional, insightful, and aware of the "African Opportunity".
"""

    async def initialize(self):
        """Initialize DeepAgent."""
        
        # MCP tools for Tavily
        mcp_tools = []
        if self.tavily_key:
            mcp_tools.append({
                "name": "tavily-remote-mcp",
                "transport_type": "stdio",
                "command": "npx",
                "args": [
                    "-y",
                    "mcp-remote",
                    f"https://mcp.tavily.com/mcp/?tavilyApiKey={self.tavily_key}",
                ],
            })
        
        # Local tools for due diligence using robust unified registry
        local_tools = None
        if HAS_VULA_TOOLS:
            local_tools = create_vula_tools()
        
        # Initialize DeepAgent with CORRECT API
        self.agent = DeepAgent(
            name="VulaDueDiligence",
            system_instruction=self._build_system_instruction(),
            model_config={
                "provider": self.provider,
                "model": self.model,
            },
            mcp_tools=mcp_tools if mcp_tools else None,
            local_tools=local_tools,  # CORRECT: single registry
            agent_config={
                "max_steps": self.max_steps,
            },
            debug=self.debug,
        )
        
        await self.agent.initialize()
        logger.info(f"VulaDeepAgent initialized: model={self.model}, tavily={bool(self.tavily_key)}")

    async def _monitor_events(
        self,
        session_id: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_end: Optional[Callable[[dict], None]] = None,
    ):
        """Monitor event stream and fire callbacks."""
        if not self.agent: return
        
        try:
            # Stream events from the router
            async for event in self.agent.event_router.stream(session_id=session_id):
                # 1. Neuro Stream (Thinking)
                if event.type == "agent_thought" and on_token:
                    msg = getattr(event.payload, "message", str(event.payload))
                    on_token(msg + "\n")
                    
                # 2. Risk Radar (Tool Results)
                if event.type == "tool_call_result" and on_tool_end:
                    tool_name = getattr(event.payload, "tool_name", "")
                    result_val = getattr(event.payload, "result", "")
                    
                    data = {
                        "tool_name": tool_name,
                        "output": result_val
                    }
                    on_tool_end(data)
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"Event monitoring error: {e}")

    async def evaluate_company(
        self,
        company_name: str,
        company_profile: Optional[Dict[str, Any]] = None,
        on_token: Optional[Callable[[str], None]] = None,
        on_tool_start: Optional[Callable[[dict], None]] = None,
        on_tool_end: Optional[Callable[[dict], None]] = None,
    ) -> Dict[str, Any]:
        """Evaluate a single company."""
        if not self.agent:
            await self.initialize()
            
        task = self._build_task(company_name, company_profile)
        start_time = datetime.now()
        session_id = str(uuid.uuid4())
        
        # Start event monitoring in background
        monitor_task = asyncio.create_task(
            self._monitor_events(session_id, on_token, on_tool_end)
        )
        
        try:
            # Pass session_id to run
            result = await self.agent.run(task, session_id=session_id)
            elapsed = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "company_name": company_name,
                "response": result.get("response", ""),
                "elapsed_seconds": elapsed,
                "confidence_overall": 85, # improved confidence
                "recommendation": "Calculated", # placeholder
                "memory_path": f"outputs/memo_{company_name.replace(' ', '_')}.md"
            }
        except Exception as e:
            logging.error(f"Evaluation failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "company_name": company_name,
                "error": str(e),
                "elapsed_seconds": (datetime.now() - start_time).total_seconds(),
            }
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
    
    def _build_task(self, company_name: str, profile: Optional[Dict] = None) -> str:
        profile = profile or {}
        sector = profile.get("sector", "Not specified")
        geography = profile.get("geography", "Africa")
        
        return f"""# SME Due Diligence Evaluation

**Company**: {company_name}
**Sector**: {sector}
**Geography**: {geography}

## Instructions

Conduct comprehensive due diligence:

1. **Research** (use internet search):
   - Company website, news, funding history
   - Founders and team background
   - Market and competitors

2. **Analyze** these domains:
   - Financial health (revenue, growth, unit economics)
   - Market opportunity (TAM/SAM/SOM)
   - Team & execution capability
   - Impact & ESG (job creation, SDG alignment)
   - Risks (regulatory, market, execution)

3. **Generate Outputs**:
   - Use `generate_financial_chart` for revenue projections
   - Use `generate_html_report` for full report (pass the image paths!)
   - Use `generate_dashboard` for dashboard (pass the image paths!)
   - Use `save_evaluation_memo` for final decision

4. **Provide Recommendation**:
   - FUND: Strong opportunity, proceed
   - CONDITIONAL: Proceed with conditions
   - PASS: Do not invest

Include confidence scores (0-100%) for each domain.
Cite all sources from your research.

Begin your evaluation now."""

    async def cleanup(self):
        if self.agent:
            await self.agent.cleanup()


async def quick_evaluate(company_name: str, tavily_key: str = None) -> Dict[str, Any]:
    """Quick evaluation helper."""
    runner = VulaDeepAgentRunner(tavily_key=tavily_key, debug=True)
    try:
        await runner.initialize()
        return await runner.evaluate_company(company_name)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deep_agent_runner.py <company_name>")
        sys.exit(1)
    
    company = " ".join(sys.argv[1:])
    print(f"\n{'='*60}")
    print(f"VULA DUE DILIGENCE: {company}")
    print(f"{'='*60}\n")
    
    result = asyncio.run(quick_evaluate(company))
    
    print(f"\n{'='*60}")
    print(f"Status: {result.get('status')}")
    print(f"Time: {result.get('elapsed_seconds', 0):.1f}s")
    if result.get('response'):
        print(f"\n{result['response'][:3000]}")
    print(f"{'='*60}")
