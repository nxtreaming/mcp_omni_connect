"""
Dashboard Screen - Main landing page for Vula TUI
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, Center
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, Label, DataTable
from textual.binding import Binding


class DashboardScreen(Screen):
    """Main dashboard screen with quick actions and recent activity."""
    
    BINDINGS = [
        Binding("1", "evaluate_single", "Single Evaluation"),
        Binding("2", "batch_evaluate", "Batch Evaluate"),
        Binding("3", "view_recent", "View Recent"),
        Binding("escape", "app.pop_screen", "Back"),
    ]
    
    def __init__(self, tavily_key: str = None, **kwargs):
        super().__init__(**kwargs)
        self.tavily_key = tavily_key
    
    def compose(self) -> ComposeResult:
        """Compose dashboard widgets."""
        yield Header()
        
        with Container(id="dashboard-container"):
            # Hero section
            with Center(id="hero"):
                yield Label(
                    "🚀 DeepAgent-Powered SME Evaluation Platform",
                    id="hero-title"
                )
                yield Label(
                    "v2.0.0 | Powered by OmniCoreAgent",
                    id="hero-subtitle"
                )
            
            # Quick Actions
            with Container(id="quick-actions"):
                yield Label("📋 Quick Actions", classes="section-title")
                with Vertical(classes="action-buttons"):
                    yield Button("🔍 Evaluate Single Company [1]", id="btn-single", variant="primary")
                    yield Button("📊 Batch Evaluate (CSV) [2]", id="btn-batch", variant="success")
                    yield Button("📁 View Recent Evaluations [3]", id="btn-recent")
                    yield Button("🔍 Search History [4]", id="btn-search")
                    yield Button("⚙️  Settings [5]", id="btn-settings")
            
            # Recent Activity Table
            with Container(id="recent-activity"):
                yield Label("📈 Recent Activity", classes="section-title")
                yield DataTable(id="recent-table")
            
            # Tips
            with Container(id="tips"):
                yield Label(
                    "💡 Tip: Press 'H' for help | 'S' for statistics",
                    classes="tip-text"
                )
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize dashboard on mount."""
        # Setup recent activity table
        table = self.query_one("#recent-table", DataTable)
        table.add_columns("Company", "Status", "Confidence", "Recommendation")
        
        # Add sample data (would load from database)
        table.add_rows([
            ("Acme AgroTech", "✅ Complete", "87%", "✅ FUND"),
            ("Lagos FinServ", "✅ Complete", "72%", "⚠️  CONDITIONAL"),
            ("Nairobi Health", "🔄 Running", "--", "--"),
        ])
        
        table.cursor_type = "row"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "btn-single":
            self.action_evaluate_single()
        elif button_id == "btn-batch":
            self.action_batch_evaluate()
        elif button_id == "btn-recent":
            self.action_view_recent()
        elif button_id == "btn-search":
            self.app.notify("Search feature coming soon!", severity="info")
        elif button_id == "btn-settings":
            self.app.notify("Settings feature coming soon!", severity="info")
    
    def action_evaluate_single(self) -> None:
        """Launch single company evaluation."""
        from .evaluation import EvaluationScreen
        self.app.push_screen(EvaluationScreen(tavily_key=self.tavily_key))
    
    def action_batch_evaluate(self) -> None:
        """Launch batch evaluation."""
        from .batch import BatchProcessingScreen
        self.app.push_screen(BatchProcessingScreen(tavily_key=self.tavily_key))
    
    def action_view_recent(self) -> None:
        """View recent evaluations."""
        self.app.notify("Recent evaluations feature coming soon!", severity="info")
