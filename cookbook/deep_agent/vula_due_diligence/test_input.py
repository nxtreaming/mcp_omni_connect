#!/usr/bin/env python3
"""
Minimal test of Textual Input widget to verify it works
"""

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Input, Button, Label, Static
from textual.binding import Binding


class TestApp(App):
    """Simple test app"""
    
    BINDINGS = [
        Binding("escape", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Vertical():
            yield Label("Test Input Field")
            yield Label("Type something below and press Enter or click button")
            yield Input(placeholder="Type here...", id="test-input")
            yield Button("Submit", id="btn-submit", variant="primary")
            yield Static("Nothing submitted yet", id="result")
        
        yield Footer()
    
    def on_mount(self) -> None:
        # Focus input
        self.query_one("#test-input", Input).focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-submit":
            input_widget = self.query_one("#test-input", Input)
            value = input_widget.value
            result = self.query_one("#result", Static)
            result.update(f"You typed: {value}")
            self.notify(f"Got: {value}")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value
        result = self.query_one("#result", Static)
        result.update(f"You typed (Enter): {value}")
        self.notify(f"Got: {value}")


if __name__ == "__main__":
    app = TestApp()
    app.run()
