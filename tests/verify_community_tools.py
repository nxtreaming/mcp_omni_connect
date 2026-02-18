"""
Community Tools Verification Script

Verifies that popular community tools can be:
1. Imported without errors
2. Instantiated (validates API key checking)
3. Produce valid Tool objects via get_tool()
4. Return standardized dict responses

Usage:
    python tests/verify_community_tools.py
"""

import asyncio
import os


async def verify_tools():
    print("=" * 60)
    print("COMMUNITY TOOLS VERIFICATION")
    print("=" * 60)

    passed = 0
    failed = 0

    # --- 1. Tools that need NO external deps (always available) ---
    print("\n[1] Tools with no external deps (should always work):")

    # Calculator
    try:
        from omnicoreagent.community import CalculatorTool
        calc = CalculatorTool()
        tool = calc.get_tool()
        assert tool.name, "Tool name is empty"
        result = await tool.function(expression="2 + 2")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert result["status"] == "success", f"Expected success, got {result['status']}"
        print(f"  ✅ CalculatorTool: {tool.name} → {result['data']}")
        passed += 1
    except Exception as e:
        print(f"  ❌ CalculatorTool: {e}")
        failed += 1

    # SleepTools
    try:
        from omnicoreagent.community import SleepTools
        sleep = SleepTools()
        tool = sleep.get_tool()
        assert tool.name, "Tool name is empty"
        print(f"  ✅ SleepTools: {tool.name}")
        passed += 1
    except Exception as e:
        print(f"  ❌ SleepTools: {e}")
        failed += 1

    # LocalPython
    try:
        from omnicoreagent.community import LocalPython
        python_tool = LocalPython()
        tool = python_tool.get_tool()
        result = python_tool._execute("print('hello')")
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert "hello" in result["data"]
        print(f"  ✅ LocalPython: {tool.name} → executed successfully")
        passed += 1
    except Exception as e:
        print(f"  ❌ LocalPython: {e}")
        failed += 1

    # LocalBash
    try:
        from omnicoreagent.community import LocalBash
        bash_tool = LocalBash()
        tool = bash_tool.get_tool()
        result = bash_tool._execute("echo 'hello bash'")
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert "hello bash" in result["data"]
        print(f"  ✅ LocalBash: {tool.name} → executed successfully")
        passed += 1
    except Exception as e:
        print(f"  ❌ LocalBash: {e}")
        failed += 1

    # HackerNews (no API key needed, uses httpx)
    try:
        from omnicoreagent.community import HackerNewsGetTopStories
        hn = HackerNewsGetTopStories()
        tool = hn.get_tool()
        assert tool.name == "hackernews_get_top_stories"
        print(f"  ✅ HackerNewsGetTopStories: {tool.name}")
        passed += 1
    except Exception as e:
        print(f"  ❌ HackerNewsGetTopStories: {e}")
        failed += 1

    # Wikipedia (no API key needed)
    try:
        from omnicoreagent.community import WikipediaSearchTool
        wiki = WikipediaSearchTool()
        tool = wiki.get_tool()
        assert tool.name
        print(f"  ✅ WikipediaSearchTool: {tool.name}")
        passed += 1
    except Exception as e:
        print(f"  ❌ WikipediaSearchTool: {e}")
        failed += 1

    # WebBrowserTools (just opens URL, no API key)
    try:
        from omnicoreagent.community import WebBrowserTools
        wb = WebBrowserTools()
        tool = wb.get_tool()
        assert tool.name
        print(f"  ✅ WebBrowserTools: {tool.name}")
        passed += 1
    except Exception as e:
        print(f"  ❌ WebBrowserTools: {e}")
        failed += 1

    # ArxivTool (no API key needed)
    try:
        from omnicoreagent.community import ArxivTool
        arxiv = ArxivTool()
        tool = arxiv.get_tool()
        assert tool.name
        print(f"  ✅ ArxivTool: {tool.name}")
        passed += 1
    except Exception as e:
        print(f"  ❌ ArxivTool: {e}")
        failed += 1

    # --- 2. Tools that need API keys (verify they validate correctly) ---
    print("\n[2] Tools that require API keys (checking validation):")

    api_key_tools = [
        ("TavilySearch", "TAVILY_API_KEY"),
        ("GoogleSearch", "GOOGLE_API_KEY"),
        ("PerplexitySearch", "PERPLEXITY_API_KEY"),
        ("TakoSearch", "TAKO_API_KEY"),
    ]

    for tool_name, env_var in api_key_tools:
        try:
            mod = __import__("omnicoreagent.community", fromlist=[tool_name])
            cls = getattr(mod, tool_name)

            if os.environ.get(env_var):
                instance = cls()
                tool = instance.get_tool()
                print(f"  ✅ {tool_name}: Instantiated with env var → {tool.name}")
                passed += 1
            else:
                try:
                    cls()
                    print(f"  ⚠️  {tool_name}: Instantiated WITHOUT API key (unexpected)")
                    failed += 1
                except (ValueError, TypeError):
                    print(f"  ✅ {tool_name}: Correctly rejects missing {env_var}")
                    passed += 1
        except ImportError:
            print(f"  ⏭️  {tool_name}: Skipped (optional dep not installed)")
        except Exception as e:
            print(f"  ❌ {tool_name}: {e}")
            failed += 1

    # --- Summary ---
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(verify_tools())
    exit(0 if success else 1)
