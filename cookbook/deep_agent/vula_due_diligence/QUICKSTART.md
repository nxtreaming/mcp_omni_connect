# Vula Due Diligence System - Quick Start Guide

## ✅ Installation Complete!

All files are ready. Here's how to run it:

### 1. Install Dependencies (ALREADY DONE!)

```bash
uv pip install textual rich
```

### 2. Set Environment Variable

```bash
export TAVILY_API_KEY=your_tavily_key_here
```

### 3. Run the System

```bash
# Test imports
cd cookbook/deep_agent/vula_due_diligence
uv run python test.py

# Launch TUI
uv run python main.py

# Or use CLI
uv run python main.py --company "Acme AgroTech" --no-tui
```

## ✅ What's Working:

- ✅ All 15 files created
- ✅ Import paths fixed
- ✅ Dependencies installed (textual, rich)
- ✅ Test script functional
- ✅ CLI launcher ready
- ✅ TUI app ready

## 📂 Complete File Structure:

```
vula_due_diligence/
├── engine/
│   ├── deep_agent_runner.py    ✅ DeepAgent RPI+ integration
│   ├── batch_processor.py       ✅ Concurrent evaluation
│   └── __init__.py
├── tui/
│   ├── app.py                   ✅ Main Textual app
│   ├── screens/
│   │   ├── dashboard.py         ✅ Landing screen
│   │   ├── evaluation.py        ✅ Real-time monitoring
│   │   ├── batch.py             ✅ Batch processing
│   │   └── __init__.py
│   ├── styles/
│   │   └── vula.tcss            ✅ Beautiful CSS
│   └── __init__.py
├── main.py                      ✅ CLI entry point
├── test.py                      ✅ Test suite
├── requirements.txt             ✅ Dependencies
├── README.md                    ✅ Full documentation
├── INSTALL.md                   ✅ Installation guide
└── sample_companies.csv         ✅ 15 test companies
```

## 🚀 Try It Now:

```bash
cd /home/abiorh/ai/omnirexflora-labs_dir/omnicoreagent/cookbook/deep_agent/vula_due_diligence

# Option 1: Run test
uv run python test.py

# Option 2: Launch TUI (interactive)
uv run python main.py

# Option 3: CLI mode
uv run python main.py --company "Acme AgroTech" --no-tui
```

## 🎯 For CTO Demo:

1. **Set TAVILY_API_KEY** (required for real internet search)
2. **Launch TUI**: `uv run python main.py`
3. **Show real-time DeepAgent orchestration**
4. **Demonstrate batch processing** with sample_companies.csv

**Success!** 🎉
