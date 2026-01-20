"""
Evaluation Screen - BLOOMBERG EDITION
real-time DeepAgent monitoring with "Neuro-Stream" and "Risk Radar".
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, Label, Input, Log, Digits
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich import box

class RiskMonitor(Static):
    """Live Risk Radar Component."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.risks = {}
        self.country = "Unknown"
        
    def update_data(self, country: str, risk_data: dict):
        self.country = country
        self.risks = risk_data
        self.refresh()
        
    def render(self):
        table = Table(box=box.SIMPLE_HEAVY, title=f"🚨 RISK RADAR: {self.country.upper()}", expand=True)
        table.add_column("Dimension", style="cyan")
        table.add_column("Level", style="bold")
        table.add_column("Context")
        
        if not self.risks:
            table.add_row("Waiting for Intelligence...", "-", "-")
        else:
            for dim, info in self.risks.items():
                level = info.get("level", "Unknown")
                level_color = "red" if level == "High" else "yellow" if level == "Medium" else "green"
                table.add_row(dim, Text(level, style=level_color), info.get("context", ""))
                
        return Panel(table, title="LIVE RISK MONITOR", border_style="red")

class NeuroStream(Log):
    """Stream of agent thoughts."""
    def write_thought(self, text: str):
        self.write(Text(text, style="italic green"))

class EvaluationScreen(Screen):
    """Bloomberg-style live evaluation screen."""
    
    CSS = """
    #input-section { height: auto; border-bottom: solid $accent; padding: 1; dock: top; }
    
    #main-grid {
        layout: grid;
        grid-size: 3 1;
        grid-columns: 1fr 1fr 1fr;
        height: 1fr;
    }
    
    #col-left { border-right: solid $secondary; }
    #col-mid { border-right: solid $secondary; }
    
    .panel-title { background: $primary; color: white; padding: 0 1; text-style: bold; }
    
    NeuroStream { background: #0c0c0c; color: #00ff00; border: none; }
    """
    
    BINDINGS = [Binding("escape", "cancel", "Back", show=True)]
    
    def __init__(self, tavily_key: str = None, company_name: str = None, **kwargs):
        super().__init__(**kwargs)
        self.tavily_key = tavily_key
        self.company_name = company_name
        self._is_evaluating = False
        self.risk_monitor = RiskMonitor(id="risk-monitor")
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        # Top Input Bar
        with Container(id="input-section"):
            yield Horizontal(
                Label("🏢 TARGET: ", classes="panel-title"),
                Input(placeholder="Type Company Name...", id="company-input", value=self.company_name or ""),
                Button("▶ INITIATE SCAN", id="start-btn", variant="warning"),
                classes="input-row"
            )
            
        # 3-Column Layout
        with Grid(id="main-grid"):
            # LEFT: Operations Log
            with Vertical(id="col-left"):
                yield Label(" 📋 OPERATIONS LOG ", classes="panel-title")
                yield Log(id="eval-log", auto_scroll=True)
                
            # MID: Neuro-Stream (Thoughts)
            with Vertical(id="col-mid"):
                yield Label(" 🧠 NEURO-STREAM (LIVE THOUGHTS) ", classes="panel-title")
                yield NeuroStream(id="neuro-stream", auto_scroll=True)
                
            # RIGHT: Intelligence Dashboard
            with Vertical(id="col-right"):
                yield Label(" 📡 INTELLIGENCE DASHBOARD ", classes="panel-title")
                yield self.risk_monitor
                yield Static(id="status-text", content="STATUS: IDLE")
        
        yield Footer()

    def on_mount(self):
        self.query_one("#company-input", Input).focus()
        
    def on_button_pressed(self, event):
        if event.button.id == "start-btn":
            self._start_evaluation(self.query_one("#company-input").value)
            
    def on_input_submitted(self, event):
        self._start_evaluation(event.value)

    def _start_evaluation(self, company_name):
        if not company_name.strip(): return
        if self._is_evaluating: return
        
        self.company_name = company_name
        self._is_evaluating = True
        self.query_one("#status-text").update(f"STATUS: SCANNING {company_name.upper()}...")
        asyncio.create_task(self._run_evaluation())

    async def _run_evaluation(self):
        log = self.query_one("#eval-log", Log)
        neuro = self.query_one("#neuro-stream", NeuroStream)
        
        try:
            from engine.deep_agent_runner import VulaDeepAgentRunner
            
            log.write(f"🚀 INITIALIZING AGENT FOR {self.company_name}...")
            
            runner = VulaDeepAgentRunner(tavily_key=self.tavily_key, debug=True)
            await runner.initialize()
            
            # CALLBACKS
            def on_token(text):
                neuro.write(text) # Stream into thinking log
                
            def on_tool_end(result: dict):
                # Hijack tool outputs for dashboard
                try:
                    tool_name = result.get("tool", "") or result.get("tool_name", "")
                    output = result.get("output", {}) or result.get("result", {})
                    
                    # Log tool usage
                    log.write(f"🔧 Tool Finished: {tool_name}")
                    
                    # Update Risk Radar
                    if tool_name == "assess_macro_risk":
                        # Handle if output is wrapped in a string/dict
                        if isinstance(output, str):
                            try: output = json.loads(output)
                            except: pass
                            
                        risk_data = output.get("risk_data")
                        
                        if risk_data:
                            log.write("⚡ INTELLIGENCE ACQUIRED: MACRO RISK PROFILE")
                            self.risk_monitor.update_data("African Market", risk_data)
                        else:
                            log.write("⚠ Warning: No risk data in tool output")
                            
                except Exception as e:
                    log.write(f"⚠ Dashboard Update Error: {e}")

            log.write("✅ AGENT ACTIVE. SCANNING...")
            
            # Pass callbacks (NOTE: DeepAgentRunner needs to support these args)
            result = await runner.evaluate_company(
                self.company_name,
                on_token=on_token,
                on_tool_end=on_tool_end
            )
            
            if result.get("status") == "success":
                log.write("✅ MISSION COMPLETE.")
                self.query_one("#status-text").update("STATUS: MISSION COMPLETE")
            else:
                log.write("❌ MISSION FAILED.")
                
        except Exception as e:
            log.write(f"💥 FATAL ERROR: {e}")
            import traceback
            log.write(traceback.format_exc())
            
        finally:
            self._is_evaluating = False    
            
    def action_cancel(self):
        self.app.pop_screen()
