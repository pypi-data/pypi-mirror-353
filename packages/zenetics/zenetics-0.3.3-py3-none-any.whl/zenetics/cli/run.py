import datetime
import importlib.util
import asyncio
import webbrowser
from pathlib import Path
from typing import Callable
import typer
from rich.console import Console

from zenetics.testrunners.test_runner_server import TestSuiteRunnerServer
from zenetics.testrunners.test_runner_base import GenerationError
from zenetics.utils.test_run_formatter import TestResultFormatter

from .common import handle_error
from ..utils.environment import validate_environment

console = Console()
formatter = TestResultFormatter(console)


def load_generate_function(file_path: Path) -> Callable:
    """Load the generate function from a Python file."""
    try:
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "generate"):
            raise ValueError(f"Missing 'generate' function in {file_path}")

        return module.generate

    except Exception as e:
        raise ValueError(f"Error loading generate function from {file_path}: {str(e)}")


def run_tests_server(
    test_suite_id: str,
    source_file: Path,
    output_dir: str,
    local_only: bool,
    verbose: bool,
    parallel: int = 2,
    use_async: bool = False,
    open_browser: bool = False,
) -> None:
    """
    Run tests using the specified test suite and generate function.

    Args:
        test_suite_id: ID of the test suite to run
        source_file: Path to the Python file containing the generate function
        output_dir: Directory to save output files
        local_only: If True, don't upload results to Zenetics
        verbose: Enable verbose output
        parallel: Maximum number of parallel evaluations
        use_async: Use asynchronous execution for potentially better performance
        open_browser: If True, open the test run URL in browser after completion
    """
    result_file = None

    try:
        # Validate environment first
        env_config = validate_environment()

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if verbose:
            console.print(
                f"\nLoading generate function from [cyan]{source_file}[/cyan]"
            )

        # Load the generate function
        try:
            generate_fn = load_generate_function(source_file)
        except ValueError as e:
            console.print(f"\n[red bold]✗ Failed to load generate function[/red bold]")
            console.print(f"[red]{str(e)}[/red]")
            raise typer.Exit(1)

        # Create result file name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = (
            output_path / f"{timestamp}_{source_file.stem}_{test_suite_id}_results.json"
        )

        # Initialize test runner with fail_fast=True (default)
        runner = TestSuiteRunnerServer(
            test_suite_id=test_suite_id,
            zenetics_api_key=env_config.zenetics_key,
            zenetics_api_url=env_config.zenetics_api_url,
            zenetics_portal_url=env_config.zenetics_portal_url,
            console=console,
            max_parallel=parallel,
            fail_fast=True,  # Always fail fast on generation errors
        )

        if verbose:
            console.print(f"Running test suite id: [cyan]{test_suite_id}[/cyan]")
            console.print(f"Maximum parallel evaluations: [cyan]{parallel}[/cyan]")
            console.print(
                f"Execution mode: [cyan]{'Asynchronous' if use_async else 'Synchronous'}[/cyan]"
            )
            console.print(f"Fail fast on generation errors: [cyan]True[/cyan]")

        # Run the tests with enhanced error handling
        try:
            if use_async:
                # Run asynchronously
                results, test_run_url = asyncio.run(
                    runner.run_async(
                        generate_fn=generate_fn,
                        output_file=result_file,
                        max_parallel=parallel,
                        save_to_zenetics=not local_only,
                    )
                )
            else:
                # Run synchronously
                results, test_run_url = runner.run(
                    generate_fn=generate_fn,
                    output_file=result_file,
                    max_parallel=parallel,
                    save_to_zenetics=not local_only,
                )

            # If we reach this point, the test run completed successfully
            # Print results
            console.print("\n")
            formatter.display_results(results, verbose)
            console.print(
                f"\n[green]✓[/green] Results saved in: [cyan]{result_file}[/cyan]"
            )

            if not local_only and test_run_url:
                console.print(
                    f"[green]✓[/green] View results in Zenetics: [link={test_run_url}]"
                    f"{test_run_url}[/link]"
                )

                # Open browser if requested
                if open_browser:
                    try:
                        console.print(f"[cyan]Opening test run in browser...[/cyan]")
                        webbrowser.open(test_run_url, new=2)
                        console.print("[green]✓[/green] Test run opened in browser")
                    except Exception as e:
                        console.print(
                            f"[yellow]Warning: Could not open browser: {str(e)}[/yellow]"
                        )
                        console.print(f"[yellow]Please open the URL manually[/yellow]")

                console.print("\n")
            else:
                console.print(
                    "[dim]No test run saved in Zenetics (local run only)[/dim]"
                )

        except GenerationError as e:
            # Handle generation errors specifically
            console.print(
                f"\n[red bold]✗ Test Run Failed - Generation Error[/red bold]"
            )
            console.print(f"\n[red]{str(e)}[/red]")

            console.print(f"\n[yellow]Resolution steps:[/yellow]")
            console.print(
                f"1. Check your generation function in [cyan]{source_file}[/cyan]"
            )
            console.print(f"2. Ensure it handles the failing test case input correctly")
            console.print(f"3. Verify it returns a valid Generation object with:")
            console.print(f"   - An 'output' field (required)")
            console.print(f"   - Optional 'retrieval_context' field")
            console.print(
                f"4. Test your function locally with the failing input before running the test suite"
            )
            console.print(
                f"5. Make sure your function doesn't raise unhandled exceptions"
            )

            # Clean up any partial result files that might have been created
            if result_file and result_file.exists():
                try:
                    result_file.unlink()
                    if verbose:
                        console.print(
                            f"\n[dim]Cleaned up partial result file: {result_file}[/dim]"
                        )
                except Exception:
                    pass  # Ignore cleanup errors

            raise typer.Exit(1)

        except Exception as e:
            # Handle other unexpected errors
            console.print(
                f"\n[red bold]✗ Test Run Failed - Unexpected Error[/red bold]"
            )
            console.print(
                f"[red]Unexpected error during test execution: {str(e)}[/red]"
            )
            if verbose:
                import traceback

                console.print("\n[dim]Stack trace:[/dim]")
                console.print(traceback.format_exc())

            # Clean up any partial result files
            if result_file and result_file.exists():
                try:
                    result_file.unlink()
                    if verbose:
                        console.print(
                            f"\n[dim]Cleaned up partial result file: {result_file}[/dim]"
                        )
                except Exception:
                    pass

            raise typer.Exit(1)

    except typer.Exit:
        # Re-raise Exit exceptions
        raise
    except Exception as e:
        # Handle any other top-level exceptions
        handle_error(e)


# Add this function to create the Typer command
def register_commands(app: typer.Typer) -> None:
    """Register test commands with the Typer app."""

    @app.command("run")
    def run_tests(
        test_suite_id: str = typer.Argument(..., help="ID of the test suite to run"),
        source_file: Path = typer.Argument(
            ...,
            help="Path to Python file with 'generate' function",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
        output_dir: str = typer.Option(
            "./results", "--output-dir", "-o", help="Directory to save results"
        ),
        local_only: bool = typer.Option(
            False, "--local-only", "-l", help="Don't upload results to Zenetics"
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Enable verbose output"
        ),
        parallel: int = typer.Option(
            5,
            "--parallel",
            "-p",
            help="Maximum number of parallel evaluations",
            min=1,
            max=50,
        ),
        async_mode: bool = typer.Option(
            False, "--async", "-a", help="Use asynchronous execution"
        ),
        open_browser: bool = typer.Option(
            False,
            "--open-browser",
            "-b",
            help="Open the test run URL in browser after completion",
        ),
    ):
        """
        Run tests for the specified test suite using the generate function.

        The generate function should accept a string input and return a Generation object
        with at least an 'output' field.

        Example:
            zenetics test run <test-suite-id> my_generate.py
            zenetics test run <test-suite-id> my_generate.py --open-browser
        """
        run_tests_server(
            test_suite_id=test_suite_id,
            source_file=source_file,
            output_dir=output_dir,
            local_only=local_only,
            verbose=verbose,
            parallel=parallel,
            use_async=async_mode,
            open_browser=open_browser,
        )
