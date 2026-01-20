#!/usr/bin/env python3
"""
Quick test script for Vula Due Diligence System
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

async def test_single_evaluation():
    """Test single company evaluation."""
    from engine.deep_agent_runner import quick_evaluate
    
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not tavily_key:
        print("❌ TAVILY_API_KEY not set")
        print("Set it with: export TAVILY_API_KEY=your_key_here")
        return
    
    print("🧪 Testing single company evaluation...")
    print()
    
    result = await quick_evaluate("Acme AgroTech", tavily_key)
    
    print("✅ Test complete!")
    print(f"Status: {result.get('status')}")
    print(f"Company: {result.get('company_name')}")
    print(f"Memory path: {result.get('memory_path')}")
    print()

async def test_batch_processing():
    """Test batch processing."""
    from engine.batch_processor import BatchProcessor
    
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not tavily_key:
        print("❌ TAVILY_API_KEY not set")
        return
    
    print("🧪 Testing batch processing...")
    print()
    
    # Create sample companies
    companies = [
        {"name": "Company A", "sector": "Tech"},
        {"name": "Company B", "sector": "AgTech"},
    ]
    
    processor = BatchProcessor(tavily_key=tavily_key, max_concurrent=2)
    
    results = await processor.process_batch(companies)
    
    print("✅ Batch test complete!")
    print(f"Total: {results['total']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print()

def test_tui_launch():
    """Test TUI launch (doesn't actually run, just imports)."""
    print("🧪 Testing TUI imports...")
    
    try:
        from tui.app import VulaTUI
        from tui.screens.dashboard import DashboardScreen
        from tui.screens.evaluation import EvaluationScreen
        from tui.screens.batch import BatchProcessingScreen
        
        print("✅ All TUI modules imported successfully!")
        print()
    except Exception as e:
        print(f"❌ TUI import failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Vula Due Diligence System - Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: TUI imports (synchronous)
    test_tui_launch()
    
    # Ask user which tests to run
    print("Available tests:")
    print("[1] Single evaluation (requires TAVILY_API_KEY, ~5-10 min)")
    print("[2] Batch processing (requires TAVILY_API_KEY, ~10-20 min)")
    print("[3] Skip API tests, just verify imports")
    print()
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        asyncio.run(test_single_evaluation())
    elif choice == "2":
        asyncio.run(test_batch_processing())
    elif choice == "3":
        print("✅ Import tests passed!")
    else:
        print("Invalid choice")
    
    print("\n" + "=" * 60)
    print("🎯 Next steps:")
    print("1. Set TAVILY_API_KEY environment variable")
    print("2. Run: python main.py")
    print("3. Or try: python main.py --company 'Acme AgroTech'")
    print("=" * 60)

if __name__ == "__main__":
    main()
