"""
Batch Processing Screen - Multi-company concurrent evaluation</>
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, Label, Input, DataTable, ProgressBar
from textual.binding import Binding


class BatchProcessingScreen(Screen):
    """Batch processing screen for multiple companies."""
    
    BINDINGS = [
        Binding("p", "pause_all", "Pause All"),
        Binding("r", "resume", "Resume"),
        Binding("e", "export", "Export Results"),
        Binding("escape", "app.pop_screen", "Back"),
    ]
    
    def __init__(self, tavily_key: str = None, **kwargs):
        super().__init__(**kwargs)
        self.tavily_key = tavily_key
        self._is_processing = False
        self.results = []
    
    def compose(self) -> ComposeResult:
        """Compose batch processing widgets."""
        yield Header()
        
        with Container(id="batch-container"):
            # CSV Upload Section
            with Horizontal(id="csv-upload"):
                yield Label("CSV File:")
                yield Input(placeholder="Path to CSV file...", id="input-csv")
                yield Button("Load", id="btn-load", variant="primary")
                yield Button("Start Batch", id="btn-start-batch", variant="success", disabled=True)
            
            # Configuration
            with Horizontal(id="batch-config"):
                yield Label("Max Concurrent:")
                yield Input(value="3", id="input-concurrent")
            
            # Overall Progress
            with Container(id="overall-progress"):
                yield Label("📊 Overall Progress", classes="section-title")
                yield ProgressBar(id="progress-bar", total=100)
                yield Static("⏳ Not started", id="progress-stats")
            
            # Company Status Table
            with Container(id="company-status"):
                yield Label("📋 Company Status", classes="section-title")
                yield DataTable(id="status-table")
            
            # Summary
            with Container(id="batch-summary"):
                yield Static("📊 Summary: Waiting to start...", id="summary-text")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize batch screen."""
        # Setup status table
        table = self.query_one("#status-table", DataTable)
        table.add_columns("#", "Company", "Status", "Conf %", "Decision")
        table.cursor_type = "row"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "btn-load":
            self.load_csv()
        elif button_id == "btn-start-batch":
            self.start_batch()
    
    def load_csv(self) -> None:
        """Load companies from CSV."""
        input_widget = self.query_one("#input-csv", Input)
        csv_path = input_widget.value.strip()
        
        if not csv_path:
            self.app.notify("Please enter a CSV file path", severity="warning")
            return
        
        try:
            from engine.batch_processor import BatchProcessor
            
            companies = BatchProcessor.load_from_csv(Path(csv_path))
            
            if not companies:
                self.app.notify("No valid companies found in CSV", severity="warning")
                return
            
            # Populate table
            table = self.query_one("#status-table", DataTable)
            table.clear()
            
            for i, company in enumerate(companies, 1):
                table.add_row(
                    str(i),
                    company.get("name", "Unknown"),
                    "⏳ Queued",
                    "--",
                    "--",
                )
            
            # Enable start button
            start_btn = self.query_one("#btn-start-batch", Button)
            start_btn.disabled = False
            
            self.companies = companies
            self.app.notify(f"Loaded {len(companies)} companies", severity="success")
            
        except Exception as e:
            self.app.notify(f"Error loading CSV: {str(e)}", severity="error")
    
    def start_batch(self) -> None:
        """Start batch processing."""
        if self._is_processing:
            return
        
        if not hasattr(self, 'companies') or not self.companies:
            self.app.notify("No companies loaded", severity="warning")
            return
        
        self._is_processing = True
        
        # Disable start button
        start_btn = self.query_one("#btn-start-batch", Button)
        start_btn.disabled = True
        
        # Run batch processing
        asyncio.create_task(self._run_batch())
    
    async def _run_batch(self) -> None:
        """Run batch processing."""
        from engine.batch_processor import BatchProcessor
        
        try:
            # Get concurrent limit
            concurrent_input = self.query_one("#input-concurrent", Input)
            max_concurrent = int(concurrent_input.value or 3)
            
            # Create processor
            processor = BatchProcessor(
                tavily_key=self.tavily_key,
                max_concurrent=max_concurrent,
            )
            
            # Progress callback
            async def progress_callback(company_name: str, status: str, result: dict = None):
                # Update table
                table = self.query_one("#status-table", DataTable)
                
                for row_key in table.rows:
                    row = table.get_row(row_key)
                    if row[1] == company_name:  # Match company name
                        if status == "starting":
                            table.update_cell(row_key, "Status", "🔄 Running")
                        elif status == "complete":
                            conf = result.get("confidence_overall", 0)
                            rec = result.get("recommendation", "PENDING")
                            table.update_cell(row_key, "Status", "✅ Complete")
                            table.update_cell(row_key, "Conf %", f"{conf}%")
                            table.update_cell(row_key, "Decision", rec)
                        elif status == "error":
                            table.update_cell(row_key, "Status", "❌ Error")
                        break
            
            # Process batch
            results = await processor.process_batch(
                self.companies,
                progress_callback=progress_callback,
            )
            
            # Update summary
            summary = self.query_one("#summary-text", Static)
            summary.update(
                f"📊 Summary: FUND: {len([r for r in results['results'] if r.get('recommendation') == 'FUND'])} | "
                f"PASS: {len([r for r in results['results'] if r.get('recommendation') == 'PASS'])} | "
                f"COND: {len([r for r in results['results'] if r.get('recommendation') == 'CONDITIONAL'])} | "
                f"Failed: {results['failed']}"
            )
            
            self.results = results
            self.app.notify(f"Batch complete! {results['successful']}/{results['total']} successful", severity="success")
            
        except Exception as e:
            self.app.notify(f"Batch processing error: {str(e)}", severity="error")
        
        finally:
            self._is_processing = False
            start_btn = self.query_one("#btn-start-batch", Button)
            start_btn.disabled = False
    
    def action_pause_all(self) -> None:
        """Pause all evaluations."""
        self.app.notify("Pause feature coming soon!", severity="info")
    
    def action_resume(self) -> None:
        """Resume evaluations."""
        self.app.notify("Resume feature coming soon!", severity="info")
    
    def action_export(self) -> None:
        """Export batch results."""
        if not self.results:
            self.app.notify("No results to export", severity="warning")
            return
        
        self.app.notify("Export feature coming soon!", severity="info")
