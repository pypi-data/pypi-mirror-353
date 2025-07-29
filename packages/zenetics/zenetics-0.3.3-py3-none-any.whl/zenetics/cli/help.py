from rich.console import Console

console = Console()


def show_help() -> None:
    """Show detailed help information about all commands."""
    console.print("\n[bold]Zenetics Test Runner CLI[/bold]")
    console.print(
        "A command-line tool for running and managing Zenetics test suites.\n"
    )

    # Environment Setup
    console.print("[bold yellow]Environment Setup[/bold yellow]")
    console.print("Required environment variables:")
    console.print("  [cyan]ZENETICS_API_KEY[/cyan] - Your Zenetics API key")
    console.print("\nYou can set these using:")
    console.print("  export ZENETICS_API_KEY=your_key")
    console.print("  # Or create a .env file with these variables\n")

    # Commands
    console.print("[bold yellow]Available Commands[/bold yellow]")

    # run command
    console.print("\n[bold cyan]run[/bold cyan]")
    console.print("  Run a test suite with the specified generator function")
    console.print("  Required Options:")
    console.print(
        "    [green]-t, --test-suite-id[/green]     ID of the test suite to run (integer)"
    )
    console.print(
        "    [green]-g, --generator-file[/green]    Python file containing the generate function"
    )
    console.print("  Optional Options:")
    console.print(
        "    [green]-o, --output-dir[/green]        Directory for storing test results (default: test_results)"
    )
    console.print(
        "    [green]-p, --max-parallel[/green]      Maximum parallel evaluations 1-10 (default: 5)"
    )
    console.print(
        "    [green]--local-only[/green]            Run locally without connecting to Zenetics API"
    )
    console.print("    [green]-v, --verbose[/green]           Enable verbose output")
    console.print("  Examples:")
    console.print(
        "    [italic]zenetics run --test-suite-id 123 --generator-file my_generator.py[/italic]"
    )
    console.print(
        "    [italic]zenetics run -t 456 -g ./generators/test_gen.py --verbose[/italic]"
    )
    console.print(
        "    [italic]zenetics run -t 789 -g gen.py --output-dir ./results --max-parallel 3[/italic]"
    )

    # config commands
    console.print("\n[bold cyan]config[/bold cyan]")
    console.print("  Manage configuration settings")
    console.print("  Subcommands:")
    console.print(
        "    [green]show[/green]                     Display current configuration and environment variables"
    )
    console.print("  Examples:")
    console.print("    [italic]zenetics config show[/italic]")

    # testsuite commands
    console.print("\n[bold cyan]testsuite[/bold cyan]")
    console.print("  Manage test suites")
    console.print("  Subcommands:")
    console.print(
        "    [green]list[/green]                    List all available test suites"
    )
    console.print("  Examples:")
    console.print("    [italic]zenetics testsuite list[/italic]")
    console.print("    [italic]zenetics testsuite --help[/italic]")

    # check command
    console.print("\n[bold cyan]check[/bold cyan]")
    console.print("  Verify connections to Zenetics API")
    console.print("  Options:")
    console.print("    [green]-v, --verbose[/green]           Enable verbose output")
    console.print("  Examples:")
    console.print("    [italic]zenetics check[/italic]")
    console.print("    [italic]zenetics check --verbose[/italic]")

    # version command
    console.print("\n[bold cyan]version[/bold cyan]")
    console.print("  Show the CLI version")
    console.print("  Example: [italic]zenetics version[/italic]")

    # help command
    console.print("\n[bold cyan]help[/bold cyan]")
    console.print("  Show this help message")
    console.print("  Example: [italic]zenetics help[/italic]")

    # Additional Information
    console.print("\n[bold yellow]Additional Information[/bold yellow]")
    console.print("• All commands will return non-zero exit codes on failure")
    console.print("• Test results are saved in the specified output directory")
    console.print(
        "• Generator files must be valid Python (.py) files with a generate function"
    )
    console.print("• Test suite IDs must be positive integers")
    console.print("• Use verbose mode (-v) for detailed execution information")
    console.print("• Check command is recommended before running tests")
    console.print("• Use --local-only for testing without API connectivity\n")

    # Command Usage Patterns
    console.print("[bold yellow]Common Usage Patterns[/bold yellow]")
    console.print("1. [bold]Check configuration:[/bold]")
    console.print("   [italic]zenetics config show[/italic]")
    console.print("2. [bold]Check connectivity:[/bold]")
    console.print("   [italic]zenetics check --verbose[/italic]")
    console.print("3. [bold]List available test suites:[/bold]")
    console.print("   [italic]zenetics testsuite list[/italic]")
    console.print("4. [bold]Run a test suite:[/bold]")
    console.print(
        "   [italic]zenetics run -t 123 -g my_generator.py --verbose[/italic]"
    )
    console.print("5. [bold]Run with custom settings:[/bold]")
    console.print(
        "   [italic]zenetics run -t 456 -g gen.py -o ./results --local-only[/italic]\n"
    )

    # Further Help
    console.print("[bold yellow]Further Resources[/bold yellow]")
    console.print("• Documentation: https://docs.zenetics.io")
    console.print("• Issues: https://github.com/zenetics/zenetics-sdk/issues")
    console.print("• Support: contact@zenetics.io\n")
