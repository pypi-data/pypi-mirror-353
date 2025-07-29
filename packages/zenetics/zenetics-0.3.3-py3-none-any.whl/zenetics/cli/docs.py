# src/zenetics/cli/docs.py
import webbrowser
from rich.console import Console

console = Console()

ZENETICS_DOCS_URL = "https://docs.zenetics.io/sdk/overview"


def open_docs() -> None:
    """
    Open the Zenetics SDK documentation in the default web browser.
    """
    try:
        console.print(
            f"[cyan]Opening Zenetics documentation at:[/cyan] {ZENETICS_DOCS_URL}"
        )

        # Open the URL in the default web browser
        # new=2 opens in a new tab if possible
        webbrowser.open(ZENETICS_DOCS_URL, new=2)

        console.print("[green]✓[/green] Documentation opened in your browser")

    except Exception as e:
        console.print(f"[red]Error opening documentation:[/red] {str(e)}")
        console.print(f"\n[yellow]Please visit the documentation manually at:[/yellow]")
        console.print(f"[cyan]{ZENETICS_DOCS_URL}[/cyan]")
