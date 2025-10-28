"""Deploy command for publishing FastApps projects."""

import asyncio
import json
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Load environment variables from .env file
load_dotenv()

console = Console()

# Default deployment server URL (can be overridden by FASTAPPS_DEPLOY_URL env var)
DEFAULT_DEPLOY_URL = os.getenv("FASTAPPS_DEPLOY_URL", "https://deploy.fastapps.org")


def get_config_dir():
    """Get FastApps config directory."""
    config_dir = Path.home() / ".fastapps"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_file():
    """Get config file path."""
    return get_config_dir() / "config.json"


def load_config():
    """Load configuration from file."""
    config_file = get_config_file()
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
    return {}


def save_config(config):
    """Save configuration to file."""
    import os

    config_file = get_config_file()
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        # Set restrictive permissions (owner read/write only)
        os.chmod(config_file, 0o600)
        return True
    except Exception as e:
        console.print(f"[red]Error: Could not save config: {e}[/red]")
        return False


def get_deploy_url() -> str:
    """
    Get deployment server URL from environment variable or default.

    Returns:
        Deployment server URL
    """
    return DEFAULT_DEPLOY_URL


def get_deploy_token() -> str:
    """
    Get stored deployment token.

    Returns:
        Access token or None
    """
    config = load_config()
    return config.get("deploy_token")


def save_deploy_token(token: str):
    """
    Save deployment token to config.

    Args:
        token: Access token to save
    """
    config = load_config()
    config["deploy_token"] = token
    save_config(config)


async def async_deploy(
    skip_build: bool = False,
    skip_confirmation: bool = False,
):
    """
    Async deployment workflow.

    Args:
        skip_build: Skip widget build step
        skip_confirmation: Skip confirmation prompt

    Returns:
        True if successful, False otherwise
    """
    deploy_url = get_deploy_url()
    from ..deployer import ArtifactPackager, ClerkOAuthAuthenticator, DeployClient

    project_root = Path.cwd()

    # Step 1: Validate project structure
    console.print("\n[cyan]Validating project structure...[/cyan]")
    try:
        packager = ArtifactPackager(project_root)
        packager._validate_project()
        console.print("[green]✓ Project structure valid[/green]")
    except FileNotFoundError as e:
        console.print(f"[red]✗ {e}[/red]")
        return False

    # Step 2: Build widgets
    if not skip_build:
        console.print("\n[cyan]Building widgets...[/cyan]")
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                capture_output=True,
                text=True,
                check=True,
            )
            console.print("[green]✓ Widgets built successfully[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗ Build failed: {e.stderr}[/red]")
            console.print(
                "[yellow]Tip: Run 'npm install' if packages are not installed[/yellow]"
            )
            return False
        except FileNotFoundError:
            console.print("[red]✗ npm not found[/red]")
            return False

    # Step 3: Show deployment summary
    console.print("\n[bold cyan]Deployment Summary[/bold cyan]")

    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Key", style="cyan")
    summary_table.add_column("Value", style="white")

    # Get project info
    try:
        package_json = json.loads((project_root / "package.json").read_text())
        project_name = package_json.get("name", "unknown")
    except Exception:
        project_name = "unknown"

    # Count widgets
    assets_dir = project_root / "assets"
    widget_count = len(list(assets_dir.glob("*.html"))) if assets_dir.exists() else 0

    summary_table.add_row("Project", project_name)
    summary_table.add_row("Widgets", str(widget_count))
    summary_table.add_row("Deploy URL", deploy_url)

    console.print(summary_table)
    console.print()

    # Step 4: Confirmation
    if not skip_confirmation:
        confirm = console.input("[bold]Deploy to production? (yes/no):[/bold] ")
        if confirm.lower() not in ["yes", "y"]:
            console.print("[yellow]Deployment cancelled[/yellow]")
            return False

    # Step 5: Authenticate
    console.print("\n[cyan]Authenticating...[/cyan]")
    token = get_deploy_token()

    if not token:
        console.print(
            "[yellow]No authentication token found. Starting OAuth flow...[/yellow]"
        )
        console.print(
            "[dim]Your browser will open for authentication. "
            "Please authorize FastApps CLI.[/dim]\n"
        )

        try:
            authenticator = ClerkOAuthAuthenticator(deploy_url)
            token = await authenticator.authenticate()
            save_deploy_token(token)
            console.print("[green]✓ Authentication successful[/green]")
        except ConnectionError as e:
            console.print(f"\n[red]✗ Connection Error[/red]\n")
            console.print(f"[yellow]Cannot connect to deployment server:[/yellow]")
            return False
        except TimeoutError as e:
            console.print(f"\n[red]✗ Authentication Timeout[/red]\n")
            console.print(
                "[yellow]Authentication took too long (5 minutes limit)[/yellow]\n"
            )
            console.print("[dim]Please try again.[/dim]")
            return False
        except RuntimeError as e:
            error_msg = str(e)
            if "OAuth error" in error_msg:
                console.print(f"\n[red]✗ OAuth Error[/red]\n")
                console.print(f"[yellow]{error_msg}[/yellow]\n")
                console.print("[dim]Please contact your deployment server administrator.[/dim]")
            elif "timed out" in error_msg.lower():
                console.print(f"\n[red]✗ Authentication Timeout[/red]\n")
                console.print(
                    "[yellow]Authentication took too long. Please try again.[/yellow]"
                )
            else:
                console.print(f"\n[red]✗ Authentication Failed[/red]\n")
                console.print(f"[yellow]{error_msg}[/yellow]")
            return False
        except Exception as e:
            console.print(f"\n[red]✗ Unexpected Error[/red]\n")
            console.print(f"[yellow]{type(e).__name__}: {e}[/yellow]\n")
            console.print(
                "[dim]If this persists, please report at: https://github.com/DooiLabs/FastApps/issues[/dim]"
            )
            return False
    else:
        console.print("[green]✓ Using saved authentication token[/green]")

    # Step 6: Package artifacts
    console.print("\n[cyan]Packaging deployment artifacts...[/cyan]")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Creating tarball...", total=None)
            tarball_path = packager.package()

        # Show tarball size
        tarball_size_mb = tarball_path.stat().st_size / (1024 * 1024)
        console.print(
            f"[green]✓ Package created ({tarball_size_mb:.2f} MB)[/green]"
        )
    except Exception as e:
        console.print(f"[red]✗ Packaging failed: {e}[/red]")
        return False

    # Step 7: Upload to server
    console.print("\n[cyan]Uploading to deployment server...[/cyan]")
    try:
        async with DeployClient(deploy_url, token) as client:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Uploading artifacts...", total=None)
                result = await client.deploy(tarball_path)

        # Clean up tarball
        tarball_path.unlink(missing_ok=True)

        if result.success:
            console.print("[green]✓ Deployment successful![/green]\n")

            # Display deployment URL
            success_panel = Panel(
                f"[bold green]Deployment URL:[/bold green]\n"
                f"[link={result.deployment_url}]{result.deployment_url}[/link]\n\n"
                f"[dim]Deployment ID: {result.deployment_id}[/dim]",
                title="🚀 Deployment Complete",
                border_style="green",
            )
            console.print(success_panel)
            return True
        else:
            # Format error message
            error_msg = result.error or "Unknown error"

            if "Authentication" in error_msg or "401" in error_msg:
                console.print(f"\n[red]✗ Authentication Failed[/red]\n")
                console.print("[yellow]Your access token is invalid or expired.[/yellow]\n")
                console.print("[dim]Clearing saved token...[/dim]")

                # Clear token
                config = load_config()
                if "deploy_token" in config:
                    del config["deploy_token"]
                    save_config(config)

                console.print("[green]Token cleared.[/green]")
                console.print("\n[cyan]Please run 'fastapps deploy' again to re-authenticate.[/cyan]")

            elif "Network" in error_msg or "Connection" in error_msg:
                console.print(f"\n[red]✗ Connection Error[/red]\n")
                console.print(f"[yellow]Cannot upload to deployment server:[/yellow]")
                console.print(f"[white]{deploy_url}[/white]\n")
                console.print(f"[dim]Error: {error_msg}[/dim]\n")
                console.print("[cyan]Possible solutions:[/cyan]")
                console.print("  • Check your internet connection")
                console.print("  • Verify the server URL is correct")
                console.print("  • Try again in a few moments")

            elif "Invalid deployment package" in error_msg:
                console.print(f"\n[red]✗ Invalid Deployment Package[/red]\n")
                console.print(f"[yellow]{error_msg}[/yellow]\n")
                console.print("[dim]Please ensure all required files are present and valid.[/dim]")

            elif "Missing required" in error_msg:
                console.print(f"\n[red]✗ Missing Required Files[/red]\n")
                console.print(f"[yellow]{error_msg}[/yellow]\n")
                console.print("[dim]Check that your project structure is complete.[/dim]")

            else:
                console.print(f"\n[red]✗ Deployment Failed[/red]\n")
                console.print(f"[yellow]{error_msg}[/yellow]")

            return False

    except ConnectionError as e:
        console.print(f"\n[red]✗ Connection Error[/red]\n")
        console.print(f"[yellow]Cannot connect to deployment server:[/yellow]")
        console.print(f"[white]{deploy_url}[/white]\n")
        console.print(f"[dim]Error: {e}[/dim]\n")
        console.print("[cyan]Please check:[/cyan]")
        console.print("  • Your internet connection")
        console.print("  • Server availability")
        console.print("  • Server URL is correct")
        return False

    except TimeoutError as e:
        console.print(f"\n[red]✗ Upload Timeout[/red]\n")
        console.print("[yellow]Upload took too long (5 minutes limit)[/yellow]\n")
        console.print("[dim]The deployment package may be too large or connection too slow.[/dim]")
        return False

    except Exception as e:
        console.print(f"\n[red]✗ Upload Failed[/red]\n")
        console.print(f"[yellow]{type(e).__name__}: {e}[/yellow]\n")
        console.print(
            "[dim]If this persists, please report at: https://github.com/DooiLabs/FastApps/issues[/dim]"
        )
        return False


def deploy_command(
    yes: bool = False,
    no_build: bool = False,
):
    """
    Deploy FastApps project to production.

    Args:
        yes: Skip confirmation prompt
        no_build: Skip widget build step
    """
    # Check if in FastApps project
    if not Path("server/main.py").exists():
        console.print("[red]Error: Not in a FastApps project directory[/red]")
        console.print(
            "[yellow]Run this command from your project root (where server/main.py exists)[/yellow]"
        )
        return False

    # Run async deployment
    try:
        success = asyncio.run(async_deploy(no_build, yes))
        return success
    except KeyboardInterrupt:
        console.print("\n[yellow]Deployment cancelled by user[/yellow]")
        return False
