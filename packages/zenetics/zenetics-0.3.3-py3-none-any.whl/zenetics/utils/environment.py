from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
import typer
from rich.console import Console
from typing import Tuple, Optional

console = Console()

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    def load_env_files():
        """Load .env files from current directory and parent directories."""
        current_path = Path.cwd()
        env_loaded = False

        # Try loading from current directory first
        env_file = current_path / ".env"
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, verbose=False, override=False)
            env_loaded = True

        # Walk up the directory tree to find .env files
        for parent in current_path.parents:
            env_file = parent / ".env"
            if env_file.exists():
                load_dotenv(dotenv_path=env_file, verbose=False, override=False)
                env_loaded = True
                break

        return env_loaded

    # Load .env files when module is imported
    _env_loaded = load_env_files()

except ImportError:
    # python-dotenv is not installed, continue without .env support
    _env_loaded = False


class EnvEnum(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


@dataclass
class EnvironmentConfig:
    zenetics_key: str
    env: EnvEnum
    zenetics_api_url: str
    zenetics_portal_url: str
    env_file_loaded: bool = False
    env_file_path: Optional[str] = None

    def __str__(self):
        return f"Environment: {self.env.value}"

    def get_masked_api_key(self) -> str:
        """Return API key with most characters masked for display."""
        if not self.zenetics_key:
            return "Not set"
        if len(self.zenetics_key) <= 8:
            return "*" * len(self.zenetics_key)
        return (
            self.zenetics_key[:4]
            + "*" * (len(self.zenetics_key) - 8)
            + self.zenetics_key[-4:]
        )


def find_env_file() -> Optional[str]:
    """Find the .env file that was loaded."""
    current_path = Path.cwd()

    # Check current directory
    env_file = current_path / ".env"
    if env_file.exists():
        return str(env_file)

    # Check parent directories
    for parent in current_path.parents:
        env_file = parent / ".env"
        if env_file.exists():
            return str(env_file)

    return None


def validate_environment() -> EnvironmentConfig:
    """Validate required environment variables."""
    zenetics_key = os.getenv("ZENETICS_API_KEY")
    environment = os.getenv("ENV")

    if not environment:
        # Default to prod
        environment = EnvEnum.PROD
    else:
        # Validate environment value
        try:
            environment = EnvEnum(environment.lower())
        except ValueError:
            console.print(
                f"[yellow]Warning: Invalid ENV value '{environment}', defaulting to 'prod'[/yellow]"
            )
            environment = EnvEnum.PROD

    missing_vars = []
    if not zenetics_key:
        missing_vars.append("ZENETICS_API_KEY")

    if missing_vars:
        console.print(
            f"[red]Error: Missing required environment "
            f"variables: {', '.join(missing_vars)}[/red]"
        )
        console.print("\nPlease set the following environment variables:")
        console.print("  [cyan]Option 1: Environment variable[/cyan]")
        console.print("    export ZENETICS_API_KEY=your_api_key")
        console.print("  [cyan]Option 2: .env file[/cyan]")
        console.print("    Create a .env file with: ZENETICS_API_KEY=your_api_key")
        raise typer.Exit(1)

    zenetics_api_url, zenetics_portal_url = get_zenetics_urls(environment)
    env_file_path = find_env_file()

    return EnvironmentConfig(
        zenetics_key=zenetics_key,
        env=environment,
        zenetics_api_url=zenetics_api_url,
        zenetics_portal_url=zenetics_portal_url,
        env_file_loaded=_env_loaded and env_file_path is not None,
        env_file_path=env_file_path,
    )


def get_zenetics_urls(env: EnvEnum) -> Tuple[str, str]:
    """
    Get Zenetics API and Portal URLs based on environment.

    Returns:
        Tuple[str, str]: Zenetics API and Portal URL
    """
    if env == EnvEnum.LOCAL:
        return "http://localhost:8080", "http://localhost:3000"
    elif env == EnvEnum.DEV:
        return "https://dev.api.zenetics.io", "https://dev.app.zenetics.io"
    elif env == EnvEnum.STAGING:
        return "https://staging.api.zenetics.io", "https://staging.app.zenetics.io"
    elif env == EnvEnum.PROD:
        return "https://api.zenetics.io", "https://app.zenetics.io"
    else:
        raise ValueError(f"Invalid environment: {env}")


def show_config() -> None:
    """Display current configuration in a formatted way."""
    try:
        config = validate_environment()

        console.print("\n[bold]ZENETICS Configuration[/bold]")
        console.print("=" * 50)

        # Environment variables
        console.print(f"[cyan]Environment (ENV):[/cyan] {config.env.value}")
        console.print(
            f"[cyan]API Key (ZENETICS_API_KEY):[/cyan] {config.get_masked_api_key()}"
        )

        # URLs
        console.print(f"[cyan]API URL:[/cyan] {config.zenetics_api_url}")
        console.print(f"[cyan]Portal URL:[/cyan] {config.zenetics_portal_url}")

        # .env file information
        if config.env_file_loaded and config.env_file_path:
            console.print(f"[green]✓ .env file loaded:[/green] {config.env_file_path}")
        else:
            console.print("[yellow]⚠ No .env file found[/yellow]")

        # Configuration source
        console.print("\n[bold]Configuration Sources:[/bold]")
        api_key_source = "Environment variable"
        env_source = "Environment variable (or default)"

        if config.env_file_loaded:
            # Check if values are likely from .env file
            if config.env_file_path:
                api_key_source = f".env file ({config.env_file_path})"
                if os.getenv("ENV"):
                    env_source = f".env file ({config.env_file_path})"

        console.print(f"  [dim]ZENETICS_API_KEY:[/dim] {api_key_source}")
        console.print(f"  [dim]ENV:[/dim] {env_source}")

        console.print()

    except typer.Exit:
        # Configuration validation failed, error already printed
        pass
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
