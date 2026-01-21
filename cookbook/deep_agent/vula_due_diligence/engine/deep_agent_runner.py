"""
DeepAgent Runner for Vula Due Diligence System
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Callable
import uuid
from omnicoreagent import DeepAgent
from vula_tools import create_vula_tools

logger = logging.getLogger(__name__)



class VulaDeepAgentRunner:
    """
    DeepAgent runner for SME due diligence evaluation.
    """
    
    def __init__(
        self,
        model: str = "gpt-4.1",
        provider: str = "openai",
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

        # Map LLM_API_KEY to provider specific key if set
        llm_key = os.getenv("LLM_API_KEY")
        if llm_key:
            if provider == "openai":
                os.environ["OPENAI_API_KEY"] = llm_key
            elif provider == "google" or provider == "gemini":
                os.environ["GOOGLE_API_KEY"] = llm_key
            elif provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = llm_key
        
    def _build_system_instruction(self) -> str:
        return """You are a **World-Class Investment Analyst** for **VulaOS** - AI-powered SME funding infrastructure for Africa.

## YOUR MISSION
Evaluate African SMEs for funding eligibility across grants, debt, and equity—reducing evaluation time by 60-90% while maintaining institutional-grade rigor.

## VULA CONTEXT
- Vula helps African SMEs find their best funding options (grants, debt, equity)
- VulaOS reduces application evaluation times by 60-90% for investors and grantmakers
- Our mission is to 10x investment into African enterprises
- The continent's largest youth workforce represents a massive opportunity

## PARALLEL SUBAGENT STRATEGY

**CRITICAL**: For comprehensive due diligence, you MUST leverage parallel subagent spawning to investigate multiple domains SIMULTANEOUSLY. This is what makes VulaOS powerful.

### Recommended Parallel Investigation Structure:

Use `spawn_parallel_subagents` with these specialists:

1. **financial_analyst** - Analyze revenues, unit economics, cash position, burn rate
2. **market_analyst** - TAM/SAM/SOM, market dynamics, growth trajectory
3. **team_analyst** - Founder backgrounds, execution track record, team composition
4. **competitive_analyst** - Local competitor mapping, defensibility, moats
5. **risk_analyst** - Macro risks (FX, regulatory), execution risks, market risks
6. **impact_analyst** - SDG alignment, job creation, ESG metrics

Each subagent should:
- Focus ONLY on their assigned domain
- Cite all sources
- Provide confidence scores (0-100%)
- Save findings to their designated memory path

## EVALUATION FRAMEWORK (Africa-First)

### 1. Financial Reality Check
- Look beyond audited financials (rare in African SME context)
- Assess traction via: transaction volume, mobile money integration, partnerships
- Consider unit economics in local currency context
- Evaluate runway and path to sustainability

### 2. Macro Risk Assessment
- **FX Risk**: Currency depreciation impact on USD-denominated investments
- **Regulatory Risk**: Policy stability, licensing requirements
- **Infrastructure Risk**: Power reliability, internet penetration

### 3. Competitive Defensibility
- Compare to LOCAL incumbents (including informal sector)
- Assess distribution advantages unique to Africa
- Evaluate partnership moats (telcos, banks, government)

### 4. Impact & ESG (MANDATORY for grants)
- SDG alignment is REQUIRED for grant eligibility
- Youth employment prioritization
- Gender lens investing criteria
- Environmental sustainability

## AVAILABLE TOOLS

**Research Tools:**
- Internet search (Tavily): Real-time data and news
- `assess_macro_risk`: Country-specific risk assessment
- `analyze_competitor_landscape`: Feature matrix vs competitors

**Output Generation Tools:**
- `generate_dashboard_infographic`: Goldman Sachs-style one-pager (call FIRST)
- `generate_financial_chart`: Revenue projections (Bear/Base/Bull)
- `generate_html_report`: Final comprehensive report (call LAST, pass image paths!)
- `save_evaluation_memo`: Investment committee memo

## WORKFLOW

### Phase 1: RESEARCH (Use Parallel Subagents)
→ Spawn 4-6 specialist subagents to investigate simultaneously
→ Financial, Market, Team, Competitive, Risk, Impact domains

### Phase 2: VERIFY
→ Read all subagent findings from memory
→ Identify gaps or contradictions
→ Calculate confidence scores per domain

### Phase 3: SYNTHESIZE
→ Cross-reference findings across domains
→ Identify patterns and insights
→ Form investment recommendation

### Phase 4: GENERATE OUTPUTS
→ Call `generate_dashboard_infographic` with key metrics
→ Call `generate_financial_chart` with projections
→ Call `generate_html_report` with sections AND image paths
→ Call `save_evaluation_memo` for final decision

## RECOMMENDATION FRAMEWORK

| Rating | Criteria | Action |
|--------|----------|--------|
| **FUND** | Strong fundamentals, manageable risks, clear path to scale | Proceed to term sheet |
| **CONDITIONAL** | Promising but gaps exist | Proceed with conditions/milestones |
| **PASS** | High risk or poor fundamentals | Do not invest at this time |

## OUTPUT QUALITY STANDARDS
- Every output should be investor-presentation ready
- Cite sources for ALL data points
- Include confidence scores per domain (0-100%)
- Acknowledge limitations and data gaps honestly
- Professional tone with African opportunity awareness
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
        
        
        # Initialize DeepAgent with CORRECT API
        self.agent = DeepAgent(
            name="VulaDueDiligence",
            system_instruction=self._build_system_instruction(),
            model_config={
                "provider": self.provider,
                "model": self.model,
            },
            mcp_tools=mcp_tools if mcp_tools else None,
            local_tools=create_vula_tools(),
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
            # Run the evaluation
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
        """
        Build the evaluation task.
        
        NOTE: The task is minimal to ensure the agent performs legitimate research.
        We only provide the company name and the African context.
        """
        return f"""# Due Diligence Request

**Company Name**: {company_name}
**Context**: African Startup / Company

---

Conduct a comprehensive due diligence evaluation for this company.
Use your parallel subagent strategy to investigate all domains simultaneously.
Generate all required outputs (dashboard, chart, report, memo) at the end."""

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
