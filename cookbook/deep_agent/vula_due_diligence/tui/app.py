"""
Vula Due Diligence TUI - Main Application

Beautiful terminal interface for SME evaluation powered by Textual.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Label
from textual.screen import Screen

from tui.screens.dashboard import DashboardScreen
from tui.screens.evaluation import EvaluationScreen
from tui.screens.batch import BatchProcessingScreen


class VulaTUI(App):
    """
    Vula Due Diligence Terminal User Interface.
    
    Features:
    - Real-time DeepAgent monitoring
    - Batch processing with progress tracking
    - Interactive results viewing
    - Beautiful visualizations
    """
    
    CSS_PATH = "styles/vula.tcss"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("h", "help", "Help", show=True),
        Binding("d", "dashboard", "Dashboard", show=True),
    ]
    
    TITLE = "Vula Due Diligence System v2.0"
    SUB_TITLE = "DeepAgent-Powered SME Evaluation Platform"
    
    def __init__(self, tavily_key: str = None, **kwargs):
        """
        Initialize Vula TUI.
        
        Args:
            tavily_key: Tavily API key for internet research
        """
        super().__init__(**kwargs)
        self.tavily_key = tavily_key or os.getenv("TAVILY_API_KEY")
        
        if not self.tavily_key:
            self.notify(
                "Warning: TAVILY_API_KEY not set. Internet research will be limited.",
                severity="warning",
                timeout=5,
            )
    
    def on_mount(self) -> None:
        """Initialize app on mount."""
        self.push_screen(DashboardScreen(tavily_key=self.tavily_key))
    
    def action_dashboard(self) -> None:
        """Navigate to dashboard."""
        self.push_screen(DashboardScreen(tavily_key=self.tavily_key))
    
    def action_help(self) -> None:
        """Show help screen."""
        self.notify(
            """
            Keyboard Shortcuts:
            
            [1] - Evaluate Single Company
            [2] - Batch Evaluate (CSV)
            [3] - View Recent Evaluations
            [H] - Show this help
            [D] - Go to Dashboard
            [Q] - Quit
            
            Use ↑↓←→ to navigate
            Use Enter to select
            Use ESC to go back
            """,
            title="Help",
            timeout=10,
        )


def run_tui(tavily_key: str = None):
    """
    Launch the Vula TUI application.
    
    Args:
        tavily_key: Optional Tavily API key
    """
    app = VulaTUI(tavily_key=tavily_key)
    app.run()


if __name__ == "__main__":
    run_tui()
