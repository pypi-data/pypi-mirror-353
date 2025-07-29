import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
import time

from rich.console import Console

from zenetics.models.evaluator import EvaluatorAssignment
from zenetics.models.generation import Generation
from zenetics.models.test_case import TestCase
from zenetics.models.test_run import EvaluatorResult
from zenetics.models.evaluation_batch import (
    EvaluatorBatch,
    EvaluatorBatchElement,
    EvaluatorBatchResult,
)
from zenetics.testrunners.test_runner_base import GenerationError, TestSuiteRunner


class TestSuiteRunnerServer(TestSuiteRunner):
    """
    Server-side implementation of TestSuiteRunner that uses
    the Zenetics API for evaluations.

    This implementation supports parallel evaluations to improve performance
    and includes robust error handling for generation function failures.
    """

    def __init__(
        self,
        test_suite_id: str,
        zenetics_api_key: str,
        zenetics_api_url: str,
        zenetics_portal_url: str,
        console: Console,
        max_parallel: int = 5,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        fail_fast: bool = True,  # Explicitly support fail_fast
    ):
        """
        Initialize the server test runner.

        Args:
            test_suite_id: ID of the test suite to run
            zenetics_api_key: Zenetics API key
            zenetics_api_url: Zenetics API host URL
            zenetics_portal_url: Zenetics portal URL
            console: Rich console for output
            max_parallel: Maximum number of parallel evaluations
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
            fail_fast: Stop execution on first generation error (default: True)
        """
        super().__init__(
            test_suite_id=test_suite_id,
            zenetics_api_key=zenetics_api_key,
            zenetics_api_url=zenetics_api_url,
            zenetics_portal_url=zenetics_portal_url,
            console=console,
            max_parallel=max_parallel,
            fail_fast=fail_fast,  # Pass fail_fast to parent
        )

        # Initialize the thread pool for parallel evaluations
        self._executor = ThreadPoolExecutor(max_workers=max_parallel)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        """Clean up resources when the object is destroyed."""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False)

    def _evaluate_generation(
        self,
        test_case: TestCase,
        generated_output: Generation,
        evaluator: EvaluatorAssignment,
    ) -> EvaluatorResult:
        """
        Evaluate a generated output using the Zenetics API.

        Args:
            test_case: The test case to evaluate against
            generated_output: Generated output from LLM
            evaluator: The evaluator assignment to use

        Returns:
            EvaluatorResult: The result of the evaluation

        Raises:
            Exception: If the evaluation fails after all retries
        """
        attempts = 0
        last_error = None

        while attempts < self.max_retries:
            try:
                return self.zenetics_api_client.evaluate(
                    test_suite_id=self.test_suite_id,
                    test_case=test_case,
                    generation=generated_output,
                    evaluator=evaluator,
                )
            except Exception as e:
                attempts += 1
                last_error = e
                if attempts < self.max_retries:
                    self.logger.warning(
                        f"Evaluation retry {attempts}/{self.max_retries} "
                        f"for test case {test_case.id} "
                        f"with evaluator {evaluator.evaluator.id}: {str(e)}"
                    )
                    # Wait before retrying
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(
                        f"Evaluation failed after {self.max_retries} attempts "
                        f"for test case {test_case.id} "
                        f"with evaluator {evaluator.evaluator.id}: {str(e)}"
                    )

        # If we get here, all attempts failed
        raise last_error

    async def _evaluate_generation_async(
        self,
        test_case: TestCase,
        generated_output: Generation,
        evaluator: EvaluatorAssignment,
    ) -> EvaluatorResult:
        """
        Evaluate a generated output asynchronously using the Zenetics API.

        This method runs the synchronous evaluation in a thread pool to avoid
        blocking the event loop.

        Args:
            test_case: The test case to evaluate against
            generated_output: Generated output from LLM
            evaluator: The evaluator assignment to use

        Returns:
            EvaluatorResult: The result of the evaluation

        Raises:
            Exception: If the evaluation fails after all retries
        """
        attempts = 0
        last_error = None

        while attempts < self.max_retries:
            try:
                # Run the synchronous evaluate method in a thread pool
                return await asyncio.to_thread(
                    self.zenetics_api_client.evaluate,
                    test_suite_id=self.test_suite_id,
                    test_case=test_case,
                    generation=generated_output,
                    evaluator=evaluator,
                )
            except Exception as e:
                attempts += 1
                last_error = e
                if attempts < self.max_retries:
                    self.logger.warning(
                        f"Async evaluation retry {attempts}/{self.max_retries} "
                        f"for test case {test_case.id} "
                        f"with evaluator {evaluator.evaluator.id}: {str(e)}"
                    )
                    # Wait before retrying
                    await asyncio.sleep(self.retry_delay)
                else:
                    self.logger.error(
                        f"Async evaluation failed after {self.max_retries} "
                        f"attempts for test case {test_case.id} "
                        f"with evaluator {evaluator.evaluator.id}: {str(e)}"
                    )

        # If we get here, all attempts failed
        raise last_error

    async def _evaluate_batch_async(
        self, batch: EvaluatorBatch, max_parallel: int = None
    ) -> EvaluatorBatchResult:
        """
        Evaluate a batch of items asynchronously with controlled concurrency.

        Args:
            batch: EvaluatorBatch containing test cases, generated outputs,
            and evaluators
            max_parallel: Maximum number of parallel evaluations

        Returns:
            EvaluatorBatchResult containing results or exceptions
        """
        max_parallel = max_parallel or self.max_parallel
        semaphore = asyncio.Semaphore(max_parallel)

        async def _evaluate_with_semaphore(element: EvaluatorBatchElement):
            """
            Helper function to evaluate a single element with semaphore control.
            """
            async with semaphore:
                try:
                    return await self._evaluate_generation_async(
                        test_case=element.test_case,
                        generated_output=element.generated_output,
                        evaluator=element.evaluator,
                    )
                except Exception as e:
                    # Return the exception instead of raising it
                    return e

        # Create tasks for all elements
        tasks = [_evaluate_with_semaphore(element) for element in batch.elements]

        # Run all tasks concurrently with limited parallelism
        results = await asyncio.gather(*tasks)
        return EvaluatorBatchResult(results=results)

    def run(
        self, generate_fn, output_file=None, max_parallel=None, save_to_zenetics=True
    ):
        """
        Run the test suite with parallel evaluations.

        Overrides the base class implementation to add the save_to_zenetics parameter
        and enhanced error handling for generation failures.

        Args:
            generate_fn: Function that generates outputs for test cases
            output_file: Optional file path to save results locally
            max_parallel: Override the default max_parallel value
            save_to_zenetics: Whether to save results to Zenetics

        Returns:
            Tuple[TestRun, Optional[str]]: TestRun object and optional Zenetics URL

        Raises:
            GenerationError: If generation function fails (propagated from base class)
        """
        test_run_url = None

        try:
            # Run the test suite - this may raise GenerationError
            test_run = super().run(
                generate_fn=generate_fn,
                output_file=output_file,
                max_parallel=max_parallel,
            )

            # Only save to Zenetics if the test run completed successfully
            if save_to_zenetics:
                try:
                    test_run_url = self.save_test_run_zenetics(test_run)
                except Exception as e:
                    self.console.print(
                        f"[red]Failed to save test run to Zenetics: {str(e)}[/red]"
                    )
                    # Don't re-raise - partial success is still useful

            return test_run, test_run_url

        except GenerationError:
            # Re-raise GenerationError without modification
            # This ensures the error propagates properly to run.py
            raise
        except Exception as e:
            # Handle any other unexpected errors
            self.console.print(f"[red]Unexpected error in test runner: {str(e)}[/red]")
            raise

    async def run_async(
        self, generate_fn, output_file=None, max_parallel=None, save_to_zenetics=True
    ):
        """
        Run the test suite asynchronously with parallel evaluations.

        Overrides the base class implementation to add the save_to_zenetics parameter
        and enhanced error handling for generation failures.

        Args:
            generate_fn: Function that generates outputs for test cases
            output_file: Optional file path to save results locally
            max_parallel: Override the default max_parallel value
            save_to_zenetics: Whether to save results to Zenetics

        Returns:
            Tuple[TestRun, Optional[str]]: TestRun object and optional Zenetics URL

        Raises:
            GenerationError: If generation function fails (propagated from base class)
        """
        test_run_url = None

        try:
            # Run the test suite asynchronously - this may raise GenerationError
            test_run = await super().run_async(
                generate_fn=generate_fn,
                output_file=output_file,
                max_parallel=max_parallel,
            )

            # Only save to Zenetics if the test run completed successfully
            if save_to_zenetics:
                try:
                    # Run in thread pool since save_test_run_zenetics is synchronous
                    test_run_url = await asyncio.to_thread(
                        self.save_test_run_zenetics, test_run
                    )
                except Exception as e:
                    self.console.print(
                        f"[red]Failed to save test run to Zenetics: {str(e)}[/red]"
                    )
                    # Don't re-raise - partial success is still useful

            return test_run, test_run_url

        except GenerationError:
            # Re-raise GenerationError without modification
            # This ensures the error propagates properly to run.py
            raise
        except Exception as e:
            # Handle any other unexpected errors
            self.console.print(
                f"[red]Unexpected error in async test runner: {str(e)}[/red]"
            )
            raise

    def _evaluate_batch(
        self, batch: EvaluatorBatch, max_parallel: int = None
    ) -> EvaluatorBatchResult:
        """
        Evaluate a batch of items in parallel using thread pool.

        Args:
            batch: EvaluatorBatch containing test cases, generated outputs,
            and evaluators
            max_parallel: Maximum number of parallel evaluations

        Returns:
            EvaluatorBatchResult containing results or exceptions
        """
        max_parallel = max_parallel or self.max_parallel

        def _evaluate_single_element(element: EvaluatorBatchElement):
            """
            Helper function to evaluate a single element for use with thread pool.
            """
            try:
                return self._evaluate_generation(
                    test_case=element.test_case,
                    generated_output=element.generated_output,
                    evaluator=element.evaluator,
                )
            except Exception as e:
                # Return the exception instead of raising it
                return e

        # Use the thread pool to run evaluations in parallel
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            # Submit all evaluation tasks
            futures = [
                executor.submit(_evaluate_single_element, element)
                for element in batch.elements
            ]

            # Collect results as they complete
            results = [future.result() for future in futures]

        return EvaluatorBatchResult(results=results)
