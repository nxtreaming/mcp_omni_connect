"""
Vula Due Diligence Tools
------------------------
Premium tools for generating financial charts, infographics, and HTML reports.
Production-grade implementation for VulaOS.
"""

import os
import logging
import json
import ast
import re
import textwrap
from datetime import datetime
from typing import Union, List, Dict, Any, Optional
import requests

def _tavily_search(query: str, max_results: int = 5) -> list:
    """Execute real-time search via Tavily API."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": False,
                "max_results": max_results
            },
            timeout=15
        )
        if response.status_code == 200:
            return response.json().get("results", [])
        return []
    except Exception as e:
        logger.error(f"Tavily search failed: {e}", exc_info=True)
        return []

from omnicoreagent import ToolRegistry

# Configure logging
logger = logging.getLogger("VulaTools")

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------

def ensure_string(content: Any) -> str:
    """
    Robustly ensure content is a string.
    Handles lists, stringified lists, and other types.
    """
    if content is None:
        return ""
        
    if isinstance(content, str):
        # Check if it looks like a stringified list ['a', 'b']
        clean_content = content.strip()
        if clean_content.startswith('[') and clean_content.endswith(']'):
            try:
                # Try to parse safely
                parsed = ast.literal_eval(clean_content)
                if isinstance(parsed, list):
                    return "\n".join(str(x) for x in parsed)
            except (ValueError, SyntaxError):
                pass
        return content
        
    if isinstance(content, list):
        return "\n".join(str(x) for x in content)
        
    return str(content)

def get_output_dir() -> str:
    """Returns the absolute path to the outputs directory."""
    # check env first
    env_dir = os.getenv("VULA_OUTPUT_DIR")
    if env_dir:
        os.makedirs(env_dir, exist_ok=True)
        return env_dir

    # Use the cookbook output directory as fallback
    base_dir = os.getcwd()
    if "cookbook" in base_dir:
        # If we are deep inside, try to find root
        while "cookbook" in os.path.basename(base_dir):
             base_dir = os.path.dirname(base_dir)
             
    output_dir = os.path.join(base_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def robust_to_html(text: str) -> str:
    """
    Convert markdown to HTML with robust fallback if markdown lib is missing.
    Matches the high-quality logic from due_diligence_tools.py.
    """
    if text:
        text = textwrap.dedent(text)
        
    try:
        import markdown
        return markdown.markdown(
            text, 
            extensions=['tables', 'fenced_code', 'sane_lists', 'smarty']
        )
    except ImportError:
        pass

    # Custom parsing logic for fallback
    # 0. Handle Code Blocks
    def replace_code_block(match):
        lang = match.group(1) or ""
        code = match.group(2).strip()
        return f'<pre><code class="language-{lang}">{code}</code></pre>'

    text = re.sub(r"```(\w*)\n(.*?)```", replace_code_block, text, flags=re.DOTALL)

    lines = text.split("\n")
    processed_lines = []
    in_list = False
    list_type = None

    for line in lines:
        stripped = line.strip()

        # Headers
        header_match = re.match(r"^(\s*)(#{1,6})\s+(.+)$", line)
        if header_match:
            if in_list:
                processed_lines.append(f"</{list_type}>")
                in_list = False
            level = len(header_match.group(2))
            content = header_match.group(3)
            processed_lines.append(f"<h{level}>{content}</h{level}>")
            continue

        # Lists
        ul_match = re.match(r"^\s*[\-\*]\s+(.+)$", line)
        ol_match = re.match(r"^\s*\d+\.\s+(.+)$", line)

        if ul_match or ol_match:
            current_type = "ul" if ul_match else "ol"
            content = ul_match.group(1) if ul_match else ol_match.group(1)

            if not in_list:
                processed_lines.append(f"<{current_type}>")
                in_list = True
                list_type = current_type
            elif list_type != current_type:
                processed_lines.append(f"</{list_type}>")
                processed_lines.append(f"<{current_type}>")
                list_type = current_type

            processed_lines.append(f"<li>{content}</li>")
            continue

        if in_list and stripped != "":
            processed_lines.append(f"</{list_type}>")
            in_list = False

        if stripped == "":
            processed_lines.append("")
        else:
            processed_lines.append(line)

    if in_list:
        processed_lines.append(f"</{list_type}>")

    html = "\n".join(processed_lines)
    
    # Inline formatting
    html = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", html)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"__(.+?)__", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    
    # Paragraph wrapping
    paragraphs = html.split("\n\n")
    final_html = []
    for p in paragraphs:
        p = p.strip()
        if not p: continue
        if p.startswith("<"):
            final_html.append(p)
        else:
            # p = p.replace("\n", "<br>\n")  <-- REMOVED: Caused bad formatting
            final_html.append(f"<p>{p}</p>")
            
    return "\n".join(final_html)

# -----------------------------------------------------------------------------
# MASTER HELPER
# -----------------------------------------------------------------------------

def create_vula_tools() -> ToolRegistry:
    """
    Creates a SINGLE registry containing ALL Vula Due Diligence tools.
    """
    registry = ToolRegistry()
    
    # Check matplotlib availability
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use("Agg") # Headless mode
        HAS_MATPLOTLIB = True
    except ImportError:
        HAS_MATPLOTLIB = False

    # ----------------- TOOL 1: HTML REPORT -----------------
    @registry.register_tool(
        name="generate_html_report",
        description="""
        Generate a professional HTML investment report (McKinsey/Goldman Sachs style).
        
        **Use this tool to:**
        - Create the final tangible output of your due diligence
        - Format findings into a beautiful, readable document
        - Impress stakeholders with professional layout
        
        **Input Format:**
        - Provide 'content' as the Executive Summary
        - Provide 'sections' dict for detailed analysis sections (Financial, Market, Team, Risks)
        - All text supports Markdown encoding
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "report_title": {"type": "string"},
                "content": {"type": "string", "description": "Executive Summary (Markdown)"},
                "sections": {
                    "type": "object",
                    "description": "Dict of Section Title -> Content (Markdown)",
                    "additionalProperties": {"type": "string"}
                },
                "dashboard_path": {"type": "string", "description": "Absolute path to the generated dashboard infographic PNG"},
                "chart_path": {"type": "string", "description": "Absolute path to the generated financial chart PNG"}
            },
            "required": ["company_name", "report_title", "content"],
        },
    )
    def generate_html_report(
        company_name: str, 
        report_title: str, 
        content: Union[str, List[Any]], 
        sections: Dict[str, str] = None,
        dashboard_path: str = None,
        chart_path: str = None
    ) -> dict:
        
        # Clean inputs
        company_name = ensure_string(company_name)
        report_title = ensure_string(report_title)
        main_content = ensure_string(content)
        
        # Sanitize paths
        if dashboard_path and (dashboard_path.startswith("N/A") or dashboard_path.lower() == "none" or "failed" in dashboard_path.lower()):
            dashboard_path = None
        if chart_path and (chart_path.startswith("N/A") or chart_path.lower() == "none" or "failed" in chart_path.lower()):
            chart_path = None
        
        # Build HTML
        html_parts = []
        
        # Header with Vula branding colors
        html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{company_name} - {report_title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Merriweather:ital,wght@0,300;0,400;0,700;1,400&display=swap');
        
        body {{ 
            font-family: 'Merriweather', serif; 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 0; 
            color: #333;
            line-height: 1.7;
            background: #fff;
        }}
        
        .header-strip {{
            background: #1a365d;
            height: 8px;
            width: 100%;
        }}
        
        .container {{ padding: 60px; }}
        
        .header {{ 
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 30px;
            margin-bottom: 40px;
        }}
        
        .meta {{
            font-family: 'Inter', sans-serif;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 1.5px;
            color: #718096;
            margin-bottom: 10px;
        }}
        
        h1 {{ 
            font-family: 'Inter', sans-serif;
            margin: 0; 
            font-size: 42px; 
            color: #1a365d; 
            letter-spacing: -1px;
            font-weight: 700;
        }}
        
        .subtitle {{ 
            font-family: 'Inter', sans-serif;
            font-size: 20px; 
            margin-top: 10px; 
            color: #4a5568; 
            font-weight: 400;
        }}
        
        h2 {{ 
            font-family: 'Inter', sans-serif;
            color: #1a365d;
            font-size: 24px;
            margin-top: 50px;
            margin-bottom: 20px;
            border-bottom: 2px solid #edf2f7;
            padding-bottom: 10px;
        }}
        
        .executive-summary {{
            background: #f8fafc;
            padding: 30px;
            border-left: 4px solid #d4af37;
            border-radius: 4px;
            margin-bottom: 40px;
        }}
        
        .executive-summary h2 {{
            margin-top: 0;
            border-bottom: none;
            font-size: 18px;
            text-transform: uppercase;
            color: #718096;
            letter-spacing: 1px;
        }}
        
        p {{ margin-bottom: 1em; }}
        
        code {{ background: #edf2f7; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
        pre {{ background: #2d3748; color: #fff; padding: 20px; border-radius: 8px; overflow-x: auto; }}
        
        table {{ width: 100%; border-collapse: collapse; margin: 30px 0; font-family: 'Inter', sans-serif; font-size: 14px; }}
        th {{ text-align: left; background: #f7fafc; padding: 12px; font-weight: 600; color: #4a5568; }}
        td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; }}
        
        .footer {{
            margin-top: 80px;
            border-top: 1px solid #e2e8f0;
            padding-top: 30px;
            text-align: center;
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            color: #cbd5e0;
        }}
    </style>
</head>
<body>
    <div class="header-strip"></div>
    <div class="container">
        <div class="header">
            <div class="meta">Investment Due Diligence Report</div>
            <h1>{company_name}</h1>
            <div class="subtitle">{report_title}</div>
            <div class="meta" style="margin-top: 20px; color: #d4af37;">
                {datetime.now().strftime('%B %d, %Y')}
            </div>
        </div>
        """)
        
        # Executive Summary
        html_parts.append('<div class="executive-summary">')
        html_parts.append('<h2>Executive Summary</h2>')
        
        # Embed Infographic if available
        if dashboard_path and os.path.exists(dashboard_path):
            rel_path = os.path.basename(dashboard_path)
            html_parts.append(f'<div style="margin-bottom: 30px; text-align: center;"><img src="{rel_path}" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"></div>')
            
        html_parts.append(robust_to_html(main_content))
        html_parts.append('</div>')
        
        # Financial Chart
        if chart_path and os.path.exists(chart_path):
            rel_path = os.path.basename(chart_path)
            html_parts.append(f'<div class="section"><h2>Financial Projections</h2><div style="text-align: center;"><img src="{rel_path}" style="max-width: 100%; border-radius: 8px; border: 1px solid #e2e8f0;"></div></div>')
        
        # Sections
        if sections:
            # Handle potential string/json inputs for sections
            if isinstance(sections, str):
                try: 
                    sections = json.loads(sections)
                except: 
                    # Fallback A: Try to parse XML-like tags <SectionName>Content</SectionName>
                    # (Common LLM artifact when asked for structured output in text mode)
                    import re
                    parsed_sections = {}
                    # Match <Tag>Content</Tag>
                    matches = re.findall(r"<([a-zA-Z0-9_]+)>\s*(.*?)\s*</\1>", sections, re.DOTALL)
                    
                    if matches:
                        for tag, tag_content in matches:
                            # Clean up tag name (Financials_and_Funding -> Financials and Funding)
                            title = tag.replace("_", " ").replace("And", "&").title()
                            parsed_sections[title] = tag_content.strip()
                        sections = parsed_sections
                    else:
                        # Fallback B: If no tags, treat entire string as one section
                        if sections.strip():
                            sections = {"Detailed Analysis": sections}
                        else:
                            sections = {}
                
            if isinstance(sections, dict):
                for title, sec_content in sections.items():
                    title = ensure_string(title)
                    sec_content = ensure_string(sec_content)
                    
                    html_parts.append(f'<div class="section">')
                    html_parts.append(f'<h2>{title}</h2>')
                    html_parts.append(robust_to_html(sec_content))
                    html_parts.append('</div>')

        # Footer
        html_parts.append(f"""
        <div class="footer">
            Generated by VulaOS DeepAgent • Confidential • {datetime.now().year}
        </div>
    </div>
</body>
</html>""")
        
        full_html = "\n".join(html_parts)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{company_name.replace(' ', '_')}_{timestamp}.html"
        filepath = os.path.join(get_output_dir(), filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_html)
            
        return {"status": "success", "filepath": filepath}

    # ----------------- TOOL 2: INFOGRAPHIC (NEW) -----------------
    @registry.register_tool(
        name="generate_dashboard_infographic",
        description="""
        Generate a professional Goldman Sachs-style investment infographic (one-pager).
        
        **Produces a high-res PNG with:**
        - Key metrics (Valuation, ARR, Growth, Market)
        - Risk Gauge (1-10)
        - Investment Recommendation Badge
        - Key Highlights
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "valuation": {"type": "string", "description": "e.g. '$50M'"},
                "arr": {"type": "string", "description": "e.g. '$1.2M'"},
                "growth_rate": {"type": "string", "description": "e.g. '120%'"},
                "market_size": {"type": "string", "description": "e.g. '$5B'"},
                "risk_score": {"type": "number", "description": "1 (Safe) - 10 (Risky)"},
                "recommendation": {"type": "string", "enum": ["BUY", "HOLD", "PASS"]},
                "key_highlights": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["company_name", "valuation", "arr", "growth_rate", "market_size", "risk_score", "recommendation"]
        },
    )
    def generate_dashboard_infographic(
        company_name: str,
        valuation: str,
        arr: str,
        growth_rate: str,
        market_size: str,
        risk_score: float,
        recommendation: str,
        key_highlights: List[str] = None
    ) -> dict:
        if not HAS_MATPLOTLIB:
            return {"status": "error", "message": "Matplotlib required"}
            
        try:
            import numpy as np
            from matplotlib.patches import FancyBboxPatch, Circle, Wedge
            import matplotlib.patheffects as path_effects
            
            # Clean inputs
            company_name = ensure_string(company_name)
            
            # Setup Figure
            fig = plt.figure(figsize=(16, 9), facecolor='white')
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_xlim(0, 16)
            ax.set_ylim(0, 9)
            ax.axis('off')
            
            # COLORS
            DARK_BLUE = "#1a365d"
            GOLD = "#d4af37"
            WHITE = "#ffffff"
            MEDIUM_GRAY = "#6c757d"
            GREEN = "#198754"
            RED = "#dc3545"
            ORANGE = "#fd7e14"
            
            # Header
            header = FancyBboxPatch((0, 7.5), 16, 1.5, boxstyle="square,pad=0", facecolor=DARK_BLUE, edgecolor="none")
            ax.add_patch(header)
            
            ax.text(0.5, 8.25, company_name.upper(), fontsize=36, color='white', fontweight='bold', va='center')
            ax.text(0.5, 7.8, "INVESTMENT DASHBOARD", fontsize=14, color=GOLD, va='center')
            
            # Metric Cards
            def draw_card(x, label, value, color=GOLD):
                card = FancyBboxPatch((x, 5.5), 3.5, 1.8, boxstyle="round,pad=0.1", facecolor='white', edgecolor='#e2e8f0')
                ax.add_patch(card)
                # Accent bar
                ax.plot([x+0.2, x+3.3], [7.2, 7.2], color=color, linewidth=3)
                ax.text(x+1.75, 6.8, label.upper(), ha='center', fontsize=10, color='#718096')
                ax.text(x+1.75, 6.2, value, ha='center', fontsize=22, fontweight='bold', color=DARK_BLUE)
                
            draw_card(0.5, "Valuation", valuation)
            draw_card(4.4, "ARR", arr, "#48bb78")
            draw_card(8.3, "Growth", growth_rate, "#48bb78")
            draw_card(12.2, "TAM", market_size)
            
            # === PREMIUM RISK GAUGE ===
            gauge_center_x = 3.5
            gauge_center_y = 3.2
            gauge_radius = 1.8

            # Background arc
            theta_start = 180
            for i in range(10):
                segment_color = plt.cm.RdYlGn_r(i / 9)
                wedge = Wedge(
                    (gauge_center_x, gauge_center_y),
                    gauge_radius,
                    theta_start + i * 18,
                    theta_start + (i + 1) * 18,
                    width=0.4,
                    facecolor=segment_color,
                    edgecolor=WHITE,
                    linewidth=1,
                )
                ax.add_patch(wedge)

            # Needle
            try: risk_score = float(risk_score)
            except: risk_score = 5.0
            
            needle_angle = 180 + (max(1, min(10, risk_score)) - 1) * 18
            needle_rad = np.radians(needle_angle)
            needle_len = gauge_radius - 0.5
            ax.arrow(
                gauge_center_x,
                gauge_center_y,
                needle_len * np.cos(needle_rad),
                needle_len * np.sin(needle_rad),
                head_width=0.15,
                head_length=0.1,
                fc=DARK_BLUE,
                ec=DARK_BLUE,
                linewidth=2,
            )

            # Center circle
            center_circle = Circle(
                (gauge_center_x, gauge_center_y),
                0.2,
                facecolor=DARK_BLUE,
                edgecolor=WHITE,
                linewidth=2,
            )
            ax.add_patch(center_circle)

            # Risk score label
            ax.text(gauge_center_x, gauge_center_y - 1.0, "RISK SCORE", fontsize=10, color=MEDIUM_GRAY, ha="center")
            ax.text(gauge_center_x, gauge_center_y - 1.4, f"{risk_score:.1f}/10", fontsize=20, color=DARK_BLUE, fontweight="bold", ha="center")
            
            # Labels
            ax.text(gauge_center_x - gauge_radius - 0.3, gauge_center_y - 0.2, "LOW", fontsize=8, color=GREEN, fontweight="bold", ha="center")
            ax.text(gauge_center_x + gauge_radius + 0.3, gauge_center_y - 0.2, "HIGH", fontsize=8, color=RED, fontweight="bold", ha="center")
            
            # Recommendation Badge
            ax.text(12, 4.5, "RECOMMENDATION", fontsize=14, fontweight='bold', color=DARK_BLUE, ha='center')
            rec_upper = recommendation.upper()
            rec_color = GREEN if rec_upper in ["BUY", "INVEST"] else ORANGE if rec_upper in ["HOLD", "NEUTRAL"] else RED
            rec_box = FancyBboxPatch((10, 3.2), 4, 1.0, boxstyle="round,pad=0.1", facecolor=rec_color)
            ax.add_patch(rec_box)
            ax.text(12, 3.7, recommendation, ha='center', va='center', fontsize=24, fontweight='bold', color='white')
            
            # Highlights
            ax.text(0.5, 2.5, "KEY HIGHLIGHTS", fontsize=14, fontweight='bold', color=DARK_BLUE)
            y_pos = 2.0
            if key_highlights:
                # Handle possible string input
                if isinstance(key_highlights, str):
                    try: 
                        # Try parsing as python list literal
                        key_highlights = ast.literal_eval(key_highlights)
                    except:
                        # Fallback: Split by newline or comma if simple string
                        if "\n" in key_highlights:
                            key_highlights = [h.strip() for h in key_highlights.split("\n") if h.strip()]
                        elif "," in key_highlights:
                            key_highlights = [h.strip() for h in key_highlights.split(",") if h.strip()]
                        else:
                            key_highlights = [key_highlights]
                    
                for h in key_highlights[:3]:
                    ax.text(0.5, y_pos, f"• {ensure_string(h)}", fontsize=12, color='#4a5568')
                    y_pos -= 0.4
            
            # Save
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dashboard_{company_name.replace(' ', '_')}_{timestamp}.png"
            filepath = os.path.join(get_output_dir(), filename)
            plt.savefig(filepath, dpi=100, bbox_inches="tight")
            plt.close()
            
            return {"status": "success", "filepath": filepath}
            
        except Exception as e:
            logger.error(f"Infographic error: {e}")
            return {"status": "error", "message": str(e)}

    # ----------------- TOOL 3: FINANCIAL CHART -----------------
    @registry.register_tool(
        name="generate_financial_chart",
        description="Generate revenue projection chart (Bear/Base/Bull).",
        inputSchema={
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "current_arr_m": {"type": "number"},
                "bear_rates": {"type": "string"},
                "base_rates": {"type": "string"},
                "bull_rates": {"type": "string"},
            },
            "required": ["company_name", "current_arr_m", "bear_rates", "base_rates", "bull_rates"],
        },
    )
    def generate_financial_chart(
        company_name: str,
        current_arr_m: float,
        bear_rates: Union[str, List[float]],
        base_rates: Union[str, List[float]],
        bull_rates: Union[str, List[float]],
    ) -> dict:
        if not HAS_MATPLOTLIB: return {"status": "error", "message": "Matplotlib missing"}
        try:
            # Minimal implementation for brevity, logic identical to before
            def parse(r):
                if isinstance(r, list): return [float(x) for x in r]
                return [float(x) for x in str(r).split(',')]
                
            bear, base, bull = parse(bear_rates), parse(base_rates), parse(bull_rates)
            years = list(range(datetime.now().year, datetime.now().year + len(base) + 1))
            
            def proj(s, rs):
                a = [s]
                for r in rs: a.append(a[-1] * r)
                return a
                
            plt.style.use('seaborn-v0_8-whitegrid')
            fig, ax = plt.subplots(figsize=(10,6))
            ax.plot(years, proj(current_arr_m, bear), 'r--', label='Bear')
            ax.plot(years, proj(current_arr_m, base), 'b-', linewidth=2, label='Base')
            ax.plot(years, proj(current_arr_m, bull), 'g--', label='Bull')
            ax.set_title(f"Revenue Projection: {company_name}")
            ax.legend()
            
            filename = f"chart_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(get_output_dir(), filename)
            plt.savefig(filepath)
            plt.close()
            return {"status": "success", "filepath": filepath}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ----------------- TOOL 4: MEMO -----------------
    @registry.register_tool(
        name="save_evaluation_memo",
        description="Save final investment memo.",
        inputSchema={
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "recommendation": {"type": "string"},
                "confidence": {"type": "number"},
                "content": {"type": "string"},
            },
            "required": ["company_name", "recommendation", "confidence", "content"],
        },
    )
    def save_evaluation_memo(company_name: str, recommendation: str, confidence: float, content: str) -> dict:
        content = ensure_string(content)
        filename = f"memo_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(get_output_dir(), filename)
        with open(filepath, "w") as f:
            f.write(f"# Evaluation: {company_name}\n\n{content}")
        return {"status": "success", "filepath": filepath}

    # ----------------- TOOL 5: COMPETITOR ANALYSIS (NEW) -----------------
    @registry.register_tool(
        name="analyze_competitor_landscape",
        description="""
        Generates a structured Feature Matrix comparing the target company against local and global competitors.
        
        **Use this to:**
        - Identify unique value propositions (UVPs).
        - Assess defensibility in the African market context.
        
        **Output:** A Markdown table and strategic differentiation verdict.
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "sector": {"type": "string", "description": "e.g. Fintech, AgriTech"},
                "competitors": {"type": "array", "items": {"type": "string"}, "description": "List of top 3-5 competitors"},
                "key_features": {"type": "array", "items": {"type": "string"}, "description": "Key features to compare"}
            },
            "required": ["company_name", "sector", "competitors", "key_features"]
        },
    )
    def analyze_competitor_landscape(company_name: str, sector: str, competitors: List[str], key_features: List[str]) -> dict:
        # REAL RESEARCH using live Tavily search
        findings = []
        # Limit to 3 competitors to ensure speed
        for comp in competitors[:3]:
            q = f"{comp} vs {company_name} features {sector} Africa"
            results = _tavily_search(q, max_results=3)
            if results:
                findings.append(f"### {comp} Analysis (Live Data):\n" + "\n".join(results))
            else:
                findings.append(f"### {comp} Analysis:\n(No live data found)")
            
        research_text = "\n\n".join(findings)
        
        # Generate Template Table
        md_table = f"### Competitive Landscape: {sector}\n\n"
        md_table += f"| Feature | {company_name} | " + " | ".join(competitors) + " |\n"
        md_table += "|---|---|" + "---|" * len(competitors) + "\n"
        
        return {
            "status": "success",
            "data": f"RESEARCH FINDINGS:\n{research_text}\n\nTEMPLATE:\n{md_table}",
            "message": "Real-time research completed. Agent must use Findings to fill the Template."
        }

    # ----------------- TOOL 6: MACRO RISK ASSESSMENT (NEW) -----------------
    @registry.register_tool(
        name="assess_macro_risk",
        description="""
        Evaluates country-specific macro risks for African markets.
        
        **Checks:**
        - Currency Fluctuation (FX Risk)
        - Regulatory Stability
        - Infrastructure Reliability (Power/Internet)
        
        **Returns:** Risk flags (High/Medium/Low) with context.
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "Target market (e.g. Kenya, Nigeria)"},
                "sector": {"type": "string"}
            },
            "required": ["country", "sector"]
        },
    )
    def assess_macro_risk(country: str, sector: str) -> dict:
        # 1. Search Real Data
        year = datetime.now().year
        q = f"{country} macroeconomic risk {sector} {year} currency regulatory infrastructure"
        results = _tavily_search(q, max_results=5)
        context = "\n".join(results)
        
        if not context:
            # Fallback if no internet or key
            context = "No live data available. Proceeding with caution."
            fx, reg, infra = "Unknown", "Unknown", "Unknown"
        else:
            # Simple keyword heuristics (Real Data Processing)
            c = context.lower()
            fx = "High" if any(x in c for x in ["depreciation", "volatility", "crash", "weakening", "shortage"]) else "Medium"
            reg = "High" if any(x in c for x in ["uncertainty", "ban", "crackdown", "policy shift"]) else "Low"
            infra = "High" if any(x in c for x in ["outage", "blackout", "load shedding", "grid failure"]) else "Medium"
        
        report = f"### Real-Time Macro Risk: {country} ({year})\n\n**Live News Analysis**:\n{context[:800]}...\n"
        
        return {
            "status": "success",
            "risk_profile": report,
            "risk_data": {
                "FX": {"level": fx, "context": "Live Search Analysis"},
                "Regulatory": {"level": reg, "context": "Live Search Analysis"},
                "Infrastructure": {"level": infra, "context": "Live Search Analysis"}
            }
        }

    return registry
