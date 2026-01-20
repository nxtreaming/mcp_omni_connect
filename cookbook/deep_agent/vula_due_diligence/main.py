#!/usr/bin/env python3
"""
Vula Due Diligence System - Main Entry Point

Launch the TUI or run CLI commands for SME evaluation.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Ensure package is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Vula Due Diligence System - DeepAgent-Powered SME Evaluation"
    )
    
    parser.add_argument(
        "--company",
        "-c",
        help="Company name to evaluate (single evaluation mode)",
    )
    
    parser.add_argument(
        "--batch",
        "-b",
        help="Path to CSV file for batch evaluation",
    )
    
    parser.add_argument(
        "--parallel",
        "-p",
        type=int,
        default=3,
        help="Max concurrent evaluations for batch mode (default: 3)",
    )
    
    parser.add_argument(
        "--tavily-key",
        "-k",
        help="Tavily API key (or set TAVILY_API_KEY env var)",
    )
    
    parser.add_argument(
        "--no-tui",
        action="store_true",
        help="Run in CLI mode without TUI",
    )
    
    parser.add_argument(
        "--export",
        "-e",
        help="Export format (pdf, html, csv)",
    )
    
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path for export",
    )
    
    args = parser.parse_args()
    
    # Get Tavily key
    tavily_key = args.tavily_key or os.getenv("TAVILY_API_KEY")
    
    if not tavily_key:
        print("⚠️  Warning: TAVILY_API_KEY not set. Internet research will be limited.")
        print("Set it with: export TAVILY_API_KEY=your_key_here")
        print()
    
    # CLI mode
    if args.no_tui or args.company or args.batch:
        asyncio.run(cli_mode(args, tavily_key))
    else:
        # TUI mode
        tui_mode(tavily_key)


def tui_mode(tavily_key: str = None):
    """Launch TUI interface."""
    from tui.app import run_tui
    
    print("🚀 Launching Vula Due Diligence TUI...")
    print()
    
    try:
        run_tui(tavily_key=tavily_key)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()


async def cli_mode(args, tavily_key: str = None):
    """Run CLI commands."""
    from engine.deep_agent_runner import quick_evaluate
    from engine.batch_processor import batch_evaluate, BatchProcessor
    
    if args.company:
        # Single company evaluation
        print(f"🔍 Evaluating: {args.company}")
        print()
        
        result = await quick_evaluate(args.company, tavily_key)
        
        if result.get("status") == "success":
            print("✅ Evaluation completed successfully!")
            print(f"📊 Confidence: {result.get('confidence_overall', 0)}%")
            print(f"📝 Recommendation: {result.get('recommendation', 'PENDING')}")
            print(f"📁 Results: {result.get('memory_path')}")
        else:
            print(f"❌ Evaluation failed: {result.get('error')}")
    
    elif args.batch:
        # Batch evaluation
        batch_path = Path(args.batch)
        
        if not batch_path.exists():
            print(f"❌ File not found: {batch_path}")
            return
        
        print(f"📊 Batch processing: {batch_path}")
        print(f"⚙️  Max concurrent: {args.parallel}")
        print()
        
        # Load companies
        companies = BatchProcessor.load_from_csv(batch_path)
        print(f"📋 Loaded {len(companies)} companies")
        print()
        
        # Process batch
        results = await batch_evaluate(
            companies=companies,
            tavily_key=tavily_key,
            max_concurrent=args.parallel,
        )
        
        print(f"\n✅ Batch complete!")
        print(f"📊 Results: {results['successful']}/{results['total']} successful")
        print(f"⏱️  Total time: {results['elapsed_seconds']:.1f}s")
        print(f"⚡ Avg time per company: {results['avg_time_per_company']:.1f}s")
        
        # Export if requested
        if args.export and args.output:
            output_path = Path(args.output)
            
            if args.export == "csv":
                BatchProcessor.save_to_csv(results['results'], output_path)
                print(f"💾 Results exported to: {output_path}")
            else:
                print(f"⚠️  Export format '{args.export}' not yet implemented")


if __name__ == "__main__":
    main()
