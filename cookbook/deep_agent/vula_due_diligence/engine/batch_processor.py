"""
Batch Processing Engine for Vula Due Diligence

Handles concurrent evaluation of multiple companies with progress tracking.
"""

import asyncio
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from .deep_agent_runner import VulaDeepAgentRunner

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Concurrent batch processor for multiple company evaluations.
    
    Features:
    - Concurrent execution with configurable parallelism
    - Progress callbacks for real-time UI updates
    - CSV input/output support
    - Error handling and retry logic
    """
    
    def __init__(
        self,
        tavily_key: str,
        max_concurrent: int = 3,
        model: str = "gemini-2.0-flash-exp",
        debug: bool = False,
    ):
        """
        Initialize batch processor.
        
        Args:
            tavily_key: Tavily API key
            max_concurrent: Maximum concurrent evaluations
            model: LLM model to use
            debug: Enable debug logging
        """
        self.tavily_key = tavily_key
        self.max_concurrent = max_concurrent
        self.model = model
        self.debug = debug
        
        self.results: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        
    async def process_batch(
        self,
        companies: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Process batch of companies concurrently.
        
        Args:
            companies: List of company dicts with 'name' and optional profile data
            progress_callback: Optional callback(company_name, status, result)
            
        Returns:
            Batch results summary
        """
        start_time = datetime.now()
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def evaluate_with_semaphore(company: Dict[str, Any]):
            async with semaphore:
                return await self._evaluate_single(company, progress_callback)
        
        # Execute all evaluations
        tasks = [evaluate_with_semaphore(company) for company in companies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Categorize results
        self.results = []
        self.errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.errors.append({
                    "company": companies[i].get("name", "Unknown"),
                    "error": str(result),
                })
            elif result.get("status") == "error":
                self.errors.append(result)
            else:
                self.results.append(result)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            "total": len(companies),
            "successful": len(self.results),
            "failed": len(self.errors),
            "results": self.results,
            "errors": self.errors,
            "elapsed_seconds": elapsed,
            "avg_time_per_company": elapsed / len(companies) if companies else 0,
        }
    
    async def _evaluate_single(
        self,
        company: Dict[str, Any],
        callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Evaluate single company with progress updates."""
        company_name = company.get("name", "Unknown")
        
        if callback:
            await callback(company_name, "starting", None)
        
        runner = VulaDeepAgentRunner(
            model=self.model,
            tavily_key=self.tavily_key,
            debug=self.debug,
        )
        
        try:
            # Extract profile if provided
            profile = {
                k: v for k, v in company.items()
                if k != "name"
            }
            
            result = await runner.evaluate_company(
                company_name=company_name,
                company_profile=profile if profile else None,
            )
            
            if callback:
                await callback(company_name, "complete", result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to evaluate {company_name}: {e}")
            error_result = {
                "status": "error",
                "company_name": company_name,
                "error": str(e),
            }
            
            if callback:
                await callback(company_name, "error", error_result)
            
            return error_result
            
        finally:
            await runner.cleanup()
    
    @staticmethod
    def load_from_csv(csv_path: Path) -> List[Dict[str, Any]]:
        """
        Load companies from CSV file.
        
        Expected columns:
        - name (required)
        - sector (optional)
        - geography (optional)
        - funding_type (optional)
        - amount_requested (optional)
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            List of company dicts
        """
        companies = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("name"):  # Must have name
                    companies.append(dict(row))
        
        return companies
    
    @staticmethod
    def save_to_csv(results: List[Dict[str, Any]], output_path: Path):
        """
        Save evaluation results to CSV.
        
        Args:
            results: List of evaluation results
            output_path: Path to output CSV
        """
        if not results:
            logger.warning("No results to save")
            return
        
        # Define output columns
        columns = [
            "company_name",
            "recommendation",
            "confidence_overall",
            "status",
            "elapsed_seconds",
            "memory_path",
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for result in results:
                row = {col: result.get(col, "") for col in columns}
                writer.writerow(row)
        
        logger.info(f"Saved {len(results)} results to {output_path}")


async def batch_evaluate(
    companies: List[Dict[str, Any]],
    tavily_key: str,
    max_concurrent: int = 3,
) -> Dict[str, Any]:
    """
    Quick batch evaluation helper.
    
    Args:
        companies: List of company dicts
        tavily_key: Tavily API key
        max_concurrent: Max parallel evaluations
        
    Returns:
        Batch results summary
    """
    processor = BatchProcessor(
        tavily_key=tavily_key,
        max_concurrent=max_concurrent,
    )
    
    return await processor.process_batch(companies)
