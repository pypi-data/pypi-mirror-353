# src/zenetics/cli/main.py
from pathlib import Path
import sys
import typer
from rich.console import Console
from typing import Optional

from zenetics.cli.run import run_tests_server
from zenetics.utils.environment import show_config

from .help import show_help
from .check import check_connections
from .testsuites import list_testsuites
from .docs import open_docs
from .common import handle_error

# Import environment handling - this will automatically load .env files

# Initialize Typer app and console
app = typer.Typer(
    name="zenetics", help="CLI for running Zenetics test suites", add_completion=False
)

console = Console()


def validate_test_suite_id(value: str) -> int:
    """Validate that test_suite_id is a valid integer."""
    try:
        test_suite_id = int(value)
        if test_suite_id <= 0:
            raise typer.BadParameter("Test suite ID must be a positive integer")
        return test_suite_id
    except ValueError:
        raise typer.BadParameter("Test suite ID must be a valid integer")


def validate_generator_file(value: str) -> Path:
    """Validate that the generator file exists and is readable."""
    if not value:
        raise typer.BadParameter("Generator file path cannot be empty")

    generator_file = Path(value)

    if not generator_file.exists():
        raise typer.BadParameter(f"Generator file does not exist: {generator_file}")

    if not generator_file.is_file():
        raise typer.BadParameter(f"Generator file path is not a file: {generator_file}")

    if not generator_file.suffix == ".py":
        raise typer.BadParameter(
            f"Generator file must be a Python (.py) file: {generator_file}"
        )

    try:
        with open(generator_file, "r") as f:
            f.read(1)  # Try to read at least one character
    except (PermissionError, OSError) as e:
        raise typer.BadParameter(
            f"Generator file is not readable: {generator_file} - {e}"
        )

    return generator_file


@app.command()
def help() -> None:
    """Show detailed help information about all commands."""
    show_help()


@app.command()
def check(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
) -> None:
    """Check connections to Zenetics API."""
    check_connections(verbose=verbose)


@app.command()
def docs() -> None:
    """Open the Zenetics SDK documentation in your web browser."""
    open_docs()


# Create a subcommand group for config operations
config_app = typer.Typer(
    name="config", help="Configuration management", add_completion=False
)

app.add_typer(config_app, name="config")


@config_app.command("show")
def config_show() -> None:
    """Show current ZENETICS configuration."""
    show_config()


# Create a subcommand group for testsuite operations
testsuite_app = typer.Typer(
    name="testsuite", help="Manage test suites", add_completion=False
)

app.add_typer(testsuite_app, name="testsuite")


@testsuite_app.command("list")
def testsuite_list() -> None:
    """List all available test suites."""
    list_testsuites()


@app.command()
def run(
    test_suite_id: Optional[str] = typer.Option(
        None,
        "--test-suite-id",
        "-t",
        help="ID of the test suite to run (required)",
        callback=lambda ctx, param, value: (
            validate_test_suite_id(value) if value else None
        ),
    ),
    generator_file: Optional[str] = typer.Option(
        None,
        "--generator-file",
        "-g",
        help="Python file containing the generate function (required)",
        callback=lambda ctx, param, value: (
            validate_generator_file(value) if value else None
        ),
    ),
    output_dir: str = typer.Option(
        "test_results", "--output-dir", "-o", help="Directory for storing test results"
    ),
    local_only: bool = typer.Option(
        False,
        "--local-only",
        help="Run the test suite locally without connecting to Zenetics API",
    ),
    max_parallel: int = typer.Option(
        5,
        "--max-parallel",
        "-p",
        help="Maximum number of parallel evaluations (1-10)",
        min=1,
        max=10,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    open_browser: bool = typer.Option(
        False,
        "--open-browser",
        "-b",
        help="Open the test run URL in browser after completion",
    ),
) -> None:
    """
    Run a test suite with the specified generator function.

    Both --test-suite-id and --generator-file are required parameters.

    Examples:
        zenetics run --test-suite-id 123 --generator-file my_generator.py
        zenetics run -t 456 -g ./generators/test_gen.py --verbose
        zenetics run --test-suite-id 789 --generator-file gen.py --output-dir ./results --max-parallel 3
        zenetics run -t 101 -g gen.py --open-browser  # Opens results in browser after completion
    """
    # Validate required parameters
    if test_suite_id is None:
        console.print("[red]Error: --test-suite-id is required[/red]")
        console.print("Use 'zenetics run --help' for more information.")
        raise typer.Exit(1)

    if generator_file is None:
        console.print("[red]Error: --generator-file is required[/red]")
        console.print("Use 'zenetics run --help' for more information.")
        raise typer.Exit(1)

    # Convert validated test_suite_id back to string for the run_tests_server function
    # (assuming the underlying function still expects a string)
    run_tests_server(
        test_suite_id=str(test_suite_id),
        source_file=generator_file,
        output_dir=output_dir,
        local_only=local_only,
        verbose=verbose,
        parallel=max_parallel,
        open_browser=open_browser,
    )


@app.command()
def version() -> None:
    """Show the version of the Zenetics CLI."""
    from importlib.metadata import version as get_version

    try:
        version = get_version("zenetics")
        console.print(f"Zenetics CLI version: {version}")
    except Exception:
        console.print("Version information not available")


def main() -> None:
    """Entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    main()
