# Vula Due Diligence - Installation & Usage Guide

## 📦 Installation

### 1. Install Dependencies

```bash
# Core dependencies
pip install textual rich

# Optional: For better performance
pip install textual[dev]
```

### 2. Set Environment Variables

```bash
# Required for internet research
export TAVILY_API_KEY=your_tavily_key_here

# Optional (if using specific LLM providers)
export GOOGLE_API_KEY=your_google_key      # For Gemini
export OPENAI_API_KEY=your_openai_key      # For OpenAI
export ANTHROPIC_API_KEY=your_anthropic_key  # For Claude
```

### 3. Get Tavily API Key

1. Go to [https://tavily.com](https://tavily.com)
2. Sign up for free account
3. Get your API key from dashboard
4. Set it: `export TAVILY_API_KEY=tvly-xxxxx`

---

## 🚀 Quick Start

### Test Installation

```bash
cd cookbook/deep_agent/vula_due_diligence
python test.py
```

### Launch TUI

```bash
# Interactive mode
python main.py

# Or use the full path
./main.py
```

### CLI Mode

```bash
# Single company evaluation
python main.py --company "Acme AgroTech"

# With custom settings
python main.py --company "Lagos FinServ" --tavily-key YOUR_KEY

# Batch processing
python main.py --batch sample_companies.csv --parallel 3

# Export results
python main.py --batch sample_companies.csv --export csv --output results.csv
```

---

## 🎯 TUI Keyboard Shortcuts

### Dashboard
- `[1]` - Evaluate Single Company
- `[2]` - Batch Evaluate (CSV)
- `[3]` - View Recent Evaluations
- `[H]` - Show Help
- `[Q]` - Quit

### Evaluation Screen
- `[P]` - Pause Evaluation
- `[S]` - Skip Current Phase
- `[ESC]` - Cancel and Go Back

### Batch Processing
- `[P]` - Pause All Evaluations
- `[R]` - Resume
- `[E]` - Export Results
- `[ESC]` - Go Back

### Navigation
- `↑↓` - Navigate lists/tables
- `←→` - Navigate sections
- `TAB` - Switch focus
- `ENTER` - Select/Confirm
- `ESC` - Go back

---

## 📊 Usage Examples

### Example 1: Quick Single Evaluation

```bash
python main.py --company "Acme AgroTech" --no-tui
```

**Output:**
```
🔍 Evaluating: Acme AgroTech

✅ Evaluation completed successfully!
📊 Confidence: 87%
📝 Recommendation: FUND
📁 Results: /memories/acme_agrotech
⏱️  Time: 5m 12s
```

### Example 2: Batch Processing

```bash
python main.py --batch sample_companies.csv --parallel 3
```

**Output:**
```
📊 Batch processing: sample_companies.csv
⚙️  Max concurrent: 3

📋 Loaded 15 companies

[Progress bars showing concurrent execution]

✅ Batch complete!
📊 Results: 15/15 successful
⏱️  Total time: 52m
⚡ Avg time per company: 3.5m
```

### Example 3: Custom CSV Format

Create `my_companies.csv`:

```csv
name,sector,geography,funding_type,amount_requested
Tech Startup Inc,SaaS,Kenya,Equity,$1.5M
Agro Farm Ltd,Agriculture,Tanzania,Grant,$200K
Mobile Money Co,Fintech,Nigeria,Debt,$500K
```

Run:

```bash
python main.py --batch my_companies.csv
```

---

## 🎨 TUI Walkthrough

### Step 1: Launch TUI

```bash
python main.py
```

You'll see the dashboard:

```
┌─ Vula Due Diligence System ─────────────────┐
│  🚀 DeepAgent-Powered SME Evaluation Platform│
│                                               │
│  [1] Evaluate Single Company                 │
│  [2] Batch Evaluate (CSV)                   │
│  [3] View Recent Evaluations                │
│                                               │
│  Recent Activity:                            │
│  Acme AgroTech    | ✅ Complete | 87% | FUND│
└───────────────────────────────────────────────┘
```

### Step 2: Single Evaluation

1. Press `1`
2. Enter company name: `"Acme AgroTech"`
3. Press `Enter`

Watch real-time execution:

```
📊 DeepAgent RPI+ Orchestration

[✓] Meta-Assessment    (Completed in 2s)
[✓] Research           (Completed in 45s)
[✓] Planning           (Completed in 8s)
[🔄] Implementing      (5/7 subagents done)

🤖 Active Subagents:
  Financial Analyst     | ✅ Complete
  Market Researcher     | 🔄 Running
  Impact Specialist     | ⏳ Queued
```

### Step 3: View Results

After completion:

```
✅ FUND - Series A Equity ($2.0M)

Confidence Breakdown:
  Financial Health    85% ████████░
  Market Opportunity  80% ████████░
  Impact & ESG        75% ███████░░
  Overall            87% ████████░ ⭐ HIGH
```

---

## 🔧 Troubleshooting

### Issue: "TAVILY_API_KEY not set"

**Solution:**
```bash
export TAVILY_API_KEY=tvly-your-key-here

# Make it permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export TAVILY_API_KEY=tvly-your-key-here' >> ~/.bashrc
source ~/.bashrc
```

### Issue: "ModuleNotFoundError: No module named 'textual'"

**Solution:**
```bash
pip install textual rich
```

### Issue: "Permission denied: ./main.py"

**Solution:**
```bash
chmod +x main.py
# Or run with python:
python main.py
```

### Issue: Evaluation is slow

**Causes & Solutions:**
1. **API rate limits**: Use `gemini-1.5-pro-latest` instead of `gemini-2.0-flash-exp`
2. **Network issues**: Check internet connection
3. **Too many subagents**: Normal for complex evaluations (5-12 agents)

### Issue: "ImportError: cannot import name 'DeepAgent'"

**Solution:**
```bash
# Make sure you're in the right directory
cd /path/to/omnicoreagent/cookbook/deep_agent/vula_due_diligence

# And that omnicoreagent is properly installed
pip install -e /path/to/omnicoreagent
```

---

## 📈 Performance Tips

### 1. Use Faster Models

```python
# In main.py, change:
model="gemini-2.0-flash-exp"  # Fast but may hit rate limits

# To:
model="gemini-1.5-pro-latest"  # More stable, still fast
```

### 2. Optimize Batch Concurrency

```bash
# More concurrent = faster but may hit API limits
python main.py --batch companies.csv --parallel 5

# Less concurrent = slower but more stable
python main.py --batch companies.csv --parallel 2
```

### 3. Cache Evaluations

The system automatically caches to avoid re-evaluating same companies.

---

## 🎭 Demo Script for CTO Meeting

```bash
# 1. Launch TUI
python main.py

# 2. Show dashboard (press H for help)

# 3. Live evaluation demo
#    - Press [1]
#    - Enter "Acme AgroTech"
#    - Watch real-time DeepAgent orchestration
#    - Show parallel subagent execution
#    - Show confidence scores

# 4. Batch processing demo
#    - Press [2]
#    - Load sample_companies.csv
#    - Start batch with 3 concurrent
#    - Show live progress tracking
#    - Export results

# Total demo time: 10-15 minutes
# Wow factor: 🔥🔥🔥
```

---

## 📚 Additional Resources

- [OmniCoreAgent Documentation](https://github.com/omnirexflora-labs/omnicoreagent)
- [Textual Documentation](https://textual.textualize.io/)
- [Tavily API Docs](https://docs.tavily.com/)
- [DeepAgent RPI+ Workflow](../../docs/deepagent_rpi.md)

---

## 🐛 Reporting Issues

Found a bug? Create an issue with:
1. Error message
2. Steps to reproduce
3. Environment (OS, Python version)
4. Log output

---

## 🎯 Next Steps

1. ✅ Test with real companies
2. ✅ Customize evaluation criteria
3. ✅ Integrate with VulaOS API
4. ✅ Add PDF/HTML export
5. ✅ Build portfolio analytics

Good luck with the CTO demo! 🚀
