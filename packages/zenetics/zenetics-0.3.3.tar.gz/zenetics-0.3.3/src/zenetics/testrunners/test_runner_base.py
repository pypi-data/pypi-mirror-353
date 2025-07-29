from abc import ABC, abstractmethod
import asyncio
import json
import time
from typing import Callable, Optional, List

from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    SpinnerColumn,
)
from rich.console import Console

from zenetics.api.zenetics_api_client import ZeneticsAPIClient
from zenetics.models.evaluator import EvaluatorAssignment
from zenetics.models.generation import Generation
from zenetics.models.test_case import TestCase
from zenetics.models.test_run import (
    EvaluationResultState,
    RunTokenUsage,
    TestRun,
    TestCaseResult,
    TestSuiteResult,
    EvaluatorResult,
)
from zenetics.models.test_suite import TestSuite
from zenetics.models.evaluation_batch import (
    EvaluatorBatch,
    EvaluatorBatchElement,
    EvaluatorBatchResult,
)


class GenerationError(Exception):
    """Custom exception for generation function errors."""

    def __init__(
        self, test_case_id: str, test_case_name: str, original_error: Exception
    ):
        self.test_case_id = test_case_id
        self.test_case_name = test_case_name
        self.original_error = original_error
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        return (
            f"Generation function failed for test case '{self.test_case_name}' "
            f"(ID: {self.test_case_id})\n"
            f"Original error: {type(self.original_error).__name__}: {str(self.original_error)}\n\n"
            f"Please check your generation function implementation and ensure it:\n"
            f"1. Handles all possible inputs correctly\n"
            f"2. Returns a valid Generation object\n"
            f"3. Doesn't raise unhandled exceptions"
        )


class TestSuiteRunner(ABC):
    """
    Abstract base class for test runners that execute test suites
    against LLM outputs.
    """

    def __init__(
        self,
        test_suite_id: str,
        zenetics_api_key: str,
        zenetics_api_url: str,
        zenetics_portal_url: str,
        console: Console,
        max_parallel: int = 5,
        fail_fast: bool = True,
    ):
        """Initialize the test runner.

        Args:
            test_suite_id: ID of the test suite to run
            zenetics_api_key: Zenetics API key
            zenetics_api_url: Zenetics API host URL
            zenetics_portal_url: Zenetics portal URL
            console: Rich console for output
            max_parallel: Maximum number of parallel evaluations
            fail_fast: Stop execution on first generation error (recommended)
        """
        self.test_suite_id = test_suite_id
        self.zenetics_api_client = ZeneticsAPIClient(
            api_key=zenetics_api_key,
            api_url=zenetics_api_url,
            portal_url=zenetics_portal_url,
        )
        self.console = console
        self.max_parallel = max_parallel
        self.fail_fast = fail_fast

    def _validate_generation_result(self, result, test_case: TestCase) -> Generation:
        """
        Validate the generation function result and provide helpful error messages.

        Args:
            result: The result from the generation function
            test_case: The test case that was processed

        Returns:
            Generation: Validated generation object

        Raises:
            GenerationError: If the result is invalid
        """
        if result is None:
            raise GenerationError(
                test_case.id,
                test_case.name,
                ValueError(
                    "Generation function returned None. Expected a Generation object."
                ),
            )

        if not isinstance(result, Generation):
            raise GenerationError(
                test_case.id,
                test_case.name,
                TypeError(
                    f"Generation function returned {type(result).__name__}. "
                    f"Expected a Generation object."
                ),
            )

        # Validate required fields
        if not hasattr(result, "output") or result.output is None:
            raise GenerationError(
                test_case.id,
                test_case.name,
                ValueError("Generation object missing required 'output' field"),
            )

        return result

    def _safe_generate(
        self, generate_fn: Callable[[str], Generation], test_case: TestCase
    ) -> Generation:
        """
        Safely call the generation function with proper error handling.

        Args:
            generate_fn: The generation function to call
            test_case: The test case to process

        Returns:
            Generation: The generated output

        Raises:
            GenerationError: If generation fails
        """
        try:
            # Call the generation function
            result = generate_fn(test_case.data.input)

            # Validate the result
            return self._validate_generation_result(result, test_case)

        except GenerationError:
            # Re-raise our custom errors as-is
            raise
        except Exception as e:
            # Wrap any other exceptions in our custom error
            raise GenerationError(test_case.id, test_case.name, e)

    async def _safe_generate_async(
        self, generate_fn: Callable[[str], Generation], test_case: TestCase
    ) -> Generation:
        """
        Safely call the generation function asynchronously with proper error handling.

        Args:
            generate_fn: The generation function to call
            test_case: The test case to process

        Returns:
            Generation: The generated output

        Raises:
            GenerationError: If generation fails
        """
        try:
            # Run generate_fn in a thread pool to avoid blocking
            result = await asyncio.to_thread(generate_fn, test_case.data.input)

            # Validate the result
            return self._validate_generation_result(result, test_case)

        except GenerationError:
            # Re-raise our custom errors as-is
            raise
        except Exception as e:
            # Wrap any other exceptions in our custom error
            raise GenerationError(test_case.id, test_case.name, e)

    @abstractmethod
    def _evaluate_generation(
        self,
        test_case: TestCase,
        generated_output: Generation,
        evaluator: EvaluatorAssignment,
    ) -> EvaluatorResult:
        """
        Evaluate a single generated output against a test case using an evaluator.

        This is the method that should be implemented by the child class to evaluate
        the generated output against the test case using the evaluator.

        Args:
            test_case: The test case to evaluate against
            generated_output: Generated output from LLM
            evaluator: The evaluator assignment to use

        Returns:
            EvaluatorResult: The result of the evaluation
        """
        pass

    @abstractmethod
    async def _evaluate_generation_async(
        self,
        test_case: TestCase,
        generated_output: Generation,
        evaluator: EvaluatorAssignment,
    ) -> EvaluatorResult:
        """
        Evaluate a single generated output asynchronously.

        Async version of _evaluate_generation that should be implemented by
        child classes that support asynchronous evaluation.

        Args:
            test_case: The test case to evaluate against
            generated_output: Generated output from LLM
            evaluator: The evaluator assignment to use

        Returns:
            EvaluatorResult: The result of the evaluation
        """
        pass

    def _evaluate_batch(
        self, batch: EvaluatorBatch, max_parallel: int = None
    ) -> EvaluatorBatchResult:
        """
        Evaluate a batch of items in parallel.

        This method uses a thread pool to run multiple evaluations in parallel.

        Args:
            batch: EvaluatorBatch containing test cases, generated outputs,
              and evaluators
            max_parallel: Maximum number of parallel evaluations

        Returns:
            EvaluatorBatchResult containing results or exceptions
        """
        max_parallel = max_parallel or self.max_parallel
        results = []

        # Simple sequential implementation - will be replaced by
        # parallel implementation in derived classes
        for element in batch.elements:
            try:
                result = self._evaluate_generation(
                    test_case=element.test_case,
                    generated_output=element.generated_output,
                    evaluator=element.evaluator,
                )
                results.append(result)
            except Exception as e:
                results.append(e)

        return EvaluatorBatchResult(results=results)

    async def _evaluate_batch_async(
        self, batch: EvaluatorBatch, max_parallel: int = None
    ) -> EvaluatorBatchResult:
        """
        Evaluate a batch of items asynchronously in parallel.

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
            async with semaphore:
                try:
                    return await self._evaluate_generation_async(
                        test_case=element.test_case,
                        generated_output=element.generated_output,
                        evaluator=element.evaluator,
                    )
                except Exception as e:
                    return e

        tasks = [_evaluate_with_semaphore(element) for element in batch.elements]
        results = await asyncio.gather(*tasks)
        return EvaluatorBatchResult(results=results)

    def run(
        self,
        generate_fn: Callable[[str], Generation],
        output_file: Optional[str] = None,
        max_parallel: int = None,
    ) -> TestRun:
        """
        Run the test suite with parallel evaluations.

        Args:
            generate_fn: Function that generates LLM outputs for inputs
            output_file: Optional path to save results locally
            max_parallel: Maximum number of parallel evaluations

        Returns:
            TestRun object containing all the results

        Raises:
            GenerationError: If generation function fails and fail_fast is True
        """
        max_parallel = max_parallel or self.max_parallel

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        )

        with progress:
            # Load suite data
            setup_task = progress.add_task(
                "[yellow]Loading test suite components...", total=3
            )
            test_suite, test_cases, evaluator_assignments = self._load_suite_data(
                progress, setup_task
            )

            # Setup progress tracking
            total_evaluations = len(test_cases) * len(evaluator_assignments)
            evaluation_task = progress.add_task(
                f"[cyan]Running {total_evaluations} "
                f"evaluations (max parallel: {max_parallel})",
                total=total_evaluations,
            )

            start_time = time.time()

            # Process test cases with enhanced error handling
            test_case_results = []
            try:
                for i, test_case in enumerate(test_cases):
                    try:
                        result = self._process_test_case(
                            test_case=test_case,
                            evaluator_assignments=evaluator_assignments,
                            generate_fn=generate_fn,
                            progress=progress,
                            progress_task=evaluation_task,
                            max_parallel=max_parallel,
                        )
                        test_case_results.append(result)
                    except GenerationError as e:
                        if self.fail_fast:
                            # Stop processing and re-raise the error
                            # The error will be handled at the CLI level with proper formatting
                            raise
                        else:
                            # Continue with failed result
                            self.console.print(f"[yellow]Warning: {str(e)}[/yellow]")
                            failed_result = self._get_failed_test_case_result(
                                test_case=test_case,
                                evaluator_assignments=evaluator_assignments,
                                reason=str(e.original_error),
                            )
                            test_case_results.append(failed_result)
                            progress.update(
                                evaluation_task, advance=len(evaluator_assignments)
                            )

                end_time = time.time()
                duration = (end_time - start_time) * 1000  # Convert to milliseconds

                progress.update(
                    evaluation_task, description="[green]Evaluations completed"
                )

                # Create test run
                test_run = self._create_test_run(
                    test_suite=test_suite,
                    test_case_results=test_case_results,
                    run_duration_ms=duration,
                )

                # Save results if needed
                if output_file:
                    save_task = progress.add_task("[yellow]Saving results...", total=1)
                    self.save_test_run_local(test_run, output_file)
                    progress.update(
                        save_task, advance=1, description="[green]Result file created"
                    )

                return test_run

            except GenerationError:
                # Re-raise GenerationError without any file saving
                raise

    async def run_async(
        self,
        generate_fn: Callable[[str], Generation],
        output_file: Optional[str] = None,
        max_parallel: int = None,
    ) -> TestRun:
        """
        Run the test suite asynchronously with parallel evaluations.

        Args:
            generate_fn: Function that generates LLM outputs for inputs
            output_file: Optional path to save results locally
            max_parallel: Maximum number of parallel evaluations

        Returns:
            TestRun object containing all the results

        Raises:
            GenerationError: If generation function fails and fail_fast is True
        """
        max_parallel = max_parallel or self.max_parallel

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        )

        with progress:
            # Load suite data
            setup_task = progress.add_task(
                "[yellow]Loading test suite components...", total=3
            )
            test_suite, test_cases, evaluator_assignments = self._load_suite_data(
                progress, setup_task
            )

            # Setup progress tracking
            total_evaluations = len(test_cases) * len(evaluator_assignments)
            evaluation_task = progress.add_task(
                f"[cyan]Running {total_evaluations} evaluations asynchronously "
                f"(max parallel: {max_parallel})",
                total=total_evaluations,
            )

            start_time = time.time()

            # Define semaphore for limiting concurrent test case generation
            generation_semaphore = asyncio.Semaphore(5)

            async def process_test_case_async(test_case):
                try:
                    async with generation_semaphore:
                        # Safely generate output with enhanced error handling
                        generated_output = await self._safe_generate_async(
                            generate_fn, test_case
                        )

                    evaluator_results = await self._run_evaluations_async(
                        test_case=test_case,
                        generated_output=generated_output,
                        evaluator_assignments=evaluator_assignments,
                        progress=progress,
                        progress_task=evaluation_task,
                        max_parallel=max_parallel,
                    )

                    return self._create_test_case_result(
                        test_case=test_case,
                        generated_output=generated_output,
                        evaluator_results=evaluator_results,
                    )

                except GenerationError as e:
                    if self.fail_fast:
                        # Re-raise to stop all processing
                        raise
                    else:
                        # Continue with failed result
                        self.console.print(f"[yellow]Warning: {str(e)}[/yellow]")
                        result = self._get_failed_test_case_result(
                            test_case=test_case,
                            evaluator_assignments=evaluator_assignments,
                            reason=str(e.original_error),
                        )
                        progress.update(
                            evaluation_task, advance=len(evaluator_assignments)
                        )
                        return result
                except Exception as e:
                    # Handle any other unexpected errors
                    error_msg = f"Unexpected error processing test case: {str(e)}"
                    self.console.print(f"[red]{error_msg}[/red]")
                    result = self._get_failed_test_case_result(
                        test_case=test_case,
                        evaluator_assignments=evaluator_assignments,
                        reason=error_msg,
                    )
                    progress.update(evaluation_task, advance=len(evaluator_assignments))
                    return result

            # Process test cases concurrently
            try:
                tasks = [process_test_case_async(test_case) for test_case in test_cases]
                test_case_results = await asyncio.gather(
                    *tasks, return_exceptions=False
                )

                end_time = time.time()
                duration = (end_time - start_time) * 1000  # Convert to milliseconds

                progress.update(
                    evaluation_task, description="[green]Evaluations completed"
                )

                # Create test run
                test_run = self._create_test_run(
                    test_suite=test_suite,
                    test_case_results=test_case_results,
                    run_duration_ms=duration,
                )

                # Save results if needed
                if output_file:
                    save_task = progress.add_task("[yellow]Saving results...", total=1)
                    self.save_test_run_local(test_run, output_file)
                    progress.update(
                        save_task, advance=1, description="[green]Result file created"
                    )

                return test_run

            except GenerationError as e:
                # Handle generation errors in async context
                # Don't print here - let the CLI level handle the error display
                raise

    def save_test_run_zenetics(self, test_run: TestRun) -> str:
        """
        Save test run results to Zenetics API.

        Args:
            test_run: TestRun object to save

        Returns:
            URL of the test run in Zenetics
        """
        test_run_url = self.zenetics_api_client.create_test_run(test_run)
        return test_run_url

    def save_test_run_local(self, test_run: TestRun, output_file: str) -> None:
        """
        Save test run results to local file.

        Args:
            test_run: TestRun object to save
            output_file: Path to save the results
        """
        with open(output_file, "w") as f:
            json.dump(test_run.model_dump(), f, indent=2)

    def _load_test_suite(self) -> TestSuite:
        """Load the test suite details from Zenetics API."""
        return self.zenetics_api_client.get_test_suite(self.test_suite_id)

    def _load_test_cases(self) -> List[TestCase]:
        """Load test cases for the test suite from Zenetics API."""
        return self.zenetics_api_client.get_test_cases(self.test_suite_id)

    def _load_evaluators(self) -> List[EvaluatorAssignment]:
        """Load evaluators assigned to the test suite from Zenetics API."""
        return self.zenetics_api_client.get_evaluators(self.test_suite_id)

    def _load_suite_data(
        self, progress: Progress, setup_task
    ) -> tuple[TestSuite, List[TestCase], List[EvaluatorAssignment]]:
        """Load all required test suite data with progress tracking."""
        test_suite = self._load_test_suite()
        progress.update(setup_task, advance=1)

        test_cases = self._load_test_cases()
        progress.update(setup_task, advance=1)

        evaluator_assignments = self._load_evaluators()
        progress.update(
            setup_task, advance=1, description="[green]Test suite data read"
        )

        return test_suite, test_cases, evaluator_assignments

    def _process_test_case(
        self,
        test_case: TestCase,
        evaluator_assignments: List[EvaluatorAssignment],
        generate_fn: Callable[[str], Generation],
        progress: Progress,
        progress_task,
        max_parallel: int = None,
    ) -> TestCaseResult:
        """Process a single test case and its evaluations with enhanced error handling."""
        # Use safe generation with enhanced error handling
        # This will raise GenerationError if generation fails - let it propagate
        generated_output = self._safe_generate(generate_fn, test_case)

        try:
            evaluator_results = self._run_evaluations(
                test_case=test_case,
                generated_output=generated_output,
                evaluator_assignments=evaluator_assignments,
                progress=progress,
                progress_task=progress_task,
                max_parallel=max_parallel,
            )

            return self._create_test_case_result(
                test_case=test_case,
                generated_output=generated_output,
                evaluator_results=evaluator_results,
            )

        except Exception as e:
            # Only catch evaluation errors, not GenerationError
            self.console.print(
                f"[red]Evaluation failed for test case {test_case.id}: {str(e)}"
            )
            result = self._get_failed_test_case_result(
                test_case=test_case,
                evaluator_assignments=evaluator_assignments,
                reason=f"Evaluation failed: {str(e)}",
            )
            progress.update(progress_task, advance=len(evaluator_assignments))
            return result

    def _run_evaluations(
        self,
        test_case: TestCase,
        generated_output: Generation,
        evaluator_assignments: List[EvaluatorAssignment],
        progress: Progress,
        progress_task,
        max_parallel: int = None,
    ) -> List[EvaluatorResult]:
        """
        Run all evaluations for a test case in parallel.

        Args:
            test_case: The test case being evaluated
            generated_output: Generated output from LLM
            evaluator_assignments: List of evaluator assignments
            progress: Progress tracker
            progress_task: Task ID for progress updates
            max_parallel: Maximum number of parallel evaluations

        Returns:
            List of EvaluatorResult objects
        """
        max_parallel = max_parallel or self.max_parallel

        # Prepare evaluation batch
        batch_elements = [
            EvaluatorBatchElement(
                test_case=test_case, generated_output=generated_output, evaluator=ea
            )
            for ea in evaluator_assignments
        ]

        batch = EvaluatorBatch(elements=batch_elements)

        # Run evaluations in parallel
        batch_result = self._evaluate_batch(batch=batch, max_parallel=max_parallel)

        # Process results and handle exceptions
        evaluator_results = []
        for i, result in enumerate(batch_result.results):
            if isinstance(result, Exception):
                self.console.print(
                    f"[red]Evaluation failed for test case {test_case.id} "
                    f"with evaluator {evaluator_assignments[i].evaluator.id}: "
                    f"{str(result)}"
                )
                evaluator_results.append(
                    self._get_failed_evaluator_result(
                        test_case=test_case,
                        evaluator=evaluator_assignments[i],
                        reason=f"Evaluation failed: {str(result)}",
                    )
                )
            else:
                evaluator_results.append(result)

            # Update progress
            progress.update(progress_task, advance=1)

        return evaluator_results

    async def _run_evaluations_async(
        self,
        test_case: TestCase,
        generated_output: Generation,
        evaluator_assignments: List[EvaluatorAssignment],
        progress: Progress,
        progress_task,
        max_parallel: int = None,
    ) -> List[EvaluatorResult]:
        """
        Run all evaluations for a test case asynchronously in parallel.

        Args:
            test_case: The test case being evaluated
            generated_output: Generated output from LLM
            evaluator_assignments: List of evaluator assignments
            progress: Progress tracker
            progress_task: Task ID for progress updates
            max_parallel: Maximum number of parallel evaluations

        Returns:
            List of EvaluatorResult objects
        """
        max_parallel = max_parallel or self.max_parallel

        # Prepare evaluation batch
        batch_elements = [
            EvaluatorBatchElement(
                test_case=test_case, generated_output=generated_output, evaluator=ea
            )
            for ea in evaluator_assignments
        ]

        batch = EvaluatorBatch(elements=batch_elements)

        # Run evaluations in parallel
        batch_result = await self._evaluate_batch_async(
            batch=batch, max_parallel=max_parallel
        )

        # Process results and handle exceptions
        evaluator_results = []
        for i, result in enumerate(batch_result.results):
            if isinstance(result, Exception):
                self.console.print(
                    f"[red]Evaluation failed for test case {test_case.id} "
                    f"with evaluator {evaluator_assignments[i].evaluator.id}: "
                    f"{str(result)}"
                )
                evaluator_results.append(
                    self._get_failed_evaluator_result(
                        test_case=test_case,
                        evaluator=evaluator_assignments[i],
                        reason=f"Evaluation failed: {str(result)}",
                    )
                )
            else:
                evaluator_results.append(result)

            # Update progress
            progress.update(progress_task, advance=1)

        return evaluator_results

    def _create_test_case_result(
        self,
        test_case: TestCase,
        generated_output: Generation,
        evaluator_results: List[EvaluatorResult],
    ) -> TestCaseResult:
        """Create a TestCaseResult from evaluator results."""
        status = EvaluationResultState.PASSED
        if any(
            er.result.state == EvaluationResultState.FAILED for er in evaluator_results
        ):
            status = EvaluationResultState.FAILED

        total_duration = sum(er.stats.duration for er in evaluator_results)

        # summarize token usage
        input_tokens = sum(er.token_usage.input_tokens for er in evaluator_results)
        completion_tokens = sum(
            er.token_usage.completion_tokens for er in evaluator_results
        )
        total_cost = sum(er.token_usage.cost for er in evaluator_results)

        return TestCaseResult(
            name=test_case.name,
            test_case_ref={
                "test_case_id": test_case.id,
                "version": test_case.version,
                "name": test_case.name,
            },
            actual_output=generated_output.output,
            retrieval_context=generated_output.retrieval_context,
            status=status,
            token_usage={
                "input_tokens": input_tokens,
                "completion_tokens": completion_tokens,
                "cost": total_cost,
            },
            stats={"duration": total_duration},
            evaluations=evaluator_results,
        )

    def _create_test_run(
        self,
        test_suite: TestSuite,
        test_case_results: List[TestCaseResult],
        run_duration_ms: float = None,
    ) -> TestRun:
        """Create the final TestRun object."""
        total_duration = sum(tc.stats.duration for tc in test_case_results)

        # summarize token usage
        input_tokens = sum(er.token_usage.input_tokens for er in test_case_results)
        completion_tokens = sum(
            er.token_usage.completion_tokens for er in test_case_results
        )
        total_cost = sum(er.token_usage.cost for er in test_case_results)

        token_usage = RunTokenUsage(
            input_tokens=input_tokens,
            completion_tokens=completion_tokens,
            cost=total_cost,
        )

        test_suite_result = TestSuiteResult(
            id=test_suite.id,
            name=test_suite.name,
            status=EvaluationResultState.PASSED,
            test_cases=test_case_results,
            token_usage=token_usage,
            stats={"duration": run_duration_ms or total_duration},
        )

        return TestRun(
            name=test_suite.name,
            token_usage=token_usage,
            stats={"duration": total_duration},
            test_suites=[test_suite_result],
        )

    def _get_failed_evaluator_result(
        self, test_case: TestCase, evaluator: EvaluatorAssignment, reason: str
    ) -> EvaluatorResult:
        """Helper function to create a failed evaluator result."""
        return EvaluatorResult(
            id=evaluator.evaluator.id,
            name=evaluator.evaluator.name,
            test_case_ref={
                "test_case_id": test_case.id,
                "version": test_case.version,
                "name": test_case.name,
            },
            threshold=evaluator.threshold,
            config=evaluator.config,
            result={
                "state": EvaluationResultState.FAILED,
                "score": 0.0,
                "reason": reason,
                "logs": "",
            },
            token_usage={"input_tokens": 0, "completion_tokens": 0, "cost": 0},
            stats={"duration": 0.0},
        )

    def _get_failed_test_case_result(
        self,
        test_case: TestCase,
        evaluator_assignments: List[EvaluatorAssignment],
        reason: str,
    ) -> TestCaseResult:
        """
        Helper function to create a failed test case result.

        This includes failed evaluator results for all evaluators.

        Args:
            test_case: The test case
            evaluator_assignments: List of evaluator assignments
            reason: Reason for failure

        Returns:
            TestCaseResult with failed evaluator results
        """
        evaluator_results = [
            self._get_failed_evaluator_result(
                test_case=test_case, evaluator=ea, reason=reason
            )
            for ea in evaluator_assignments
        ]

        return TestCaseResult(
            name=test_case.name,
            test_case_ref={
                "test_case_id": test_case.id,
                "version": test_case.version,
                "name": test_case.name,
            },
            actual_output="",
            retrieval_context=[],
            status=EvaluationResultState.FAILED,
            token_usage={"input_tokens": 0, "completion_tokens": 0, "cost": 0},
            stats={"duration": 0.0},
            evaluations=evaluator_results,
        )
