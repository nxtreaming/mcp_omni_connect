#!/bin/bash
# Complete Setup and Test Script for Vula Due Diligence System

echo "================================================================"
echo "🚀 Vula Due Diligence System - Complete Setup & Test"
echo "================================================================"
echo ""

# Step 1: Check dependencies
echo "📋 Step 1: Checking dependencies..."
if uv pip list | grep -q textual; then
    echo "✅ Textual installed"
else
    echo "❌ Textual not installed. Installing..."
    uv pip install textual rich
fi
echo ""

# Step 2: Check environment
echo "📋 Step 2: Checking environment variables..."
if [ -z "$TAVILY_API_KEY" ]; then
    echo "⚠️  TAVILY_API_KEY not set"
    echo "   Run: export TAVILY_API_KEY=your_key_here"
    echo "   Or continue without it (limited internet research)"
else
    echo "✅ TAVILY_API_KEY is set"
fi
echo ""

# Step 3: Test imports
echo "📋 Step 3: Testing imports..."
cd /home/abiorh/ai/omnirexflora-labs_dir/omnicoreagent/cookbook/deep_agent/vula_due_diligence
uv run python test.py << EOF
3
EOF
echo ""

# Step 4: Show help
echo "📋 Step 4: Showing CLI help..."
uv run python main.py --help
echo ""

# Step 5: Instructions
echo "================================================================"
echo "✅ Setup Complete! Next Steps:"
echo "================================================================"
echo ""
echo "1. Set API key (if not done):"
echo "   export TAVILY_API_KEY=your_tavily_key_here"
echo ""
echo "2. Launch TUI (interactive):"
echo "   cd cookbook/deep_agent/vula_due_diligence"
echo "   uv run python main.py"
echo ""
echo "3. Or use CLI mode:"
echo "   uv run python main.py --company 'Acme AgroTech' --no-tui"
echo ""
echo "4. Or batch process:"
echo "   uv run python main.py --batch sample_companies.csv --no-tui"
echo ""
echo "================================================================"
echo "🎯 Ready for CTO Demo!"
echo "================================================================"
