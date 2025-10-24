"""Use command - Add integrations to FastApps projects."""

from pathlib import Path
from rich.console import Console

console = Console()


METORIAL_TEMPLATE = '''"""Metorial MCP Integration for FastApps.

Setup:
  export METORIAL_API_KEY="your_metorial_api_key"
  export OPENAI_API_KEY="your_openai_api_key"
  export METORIAL_DEPLOYMENT_ID="your_deployment_id"

Then run:
  python server/api/metorial_mcp.py
"""

import os
import asyncio
from metorial import Metorial
from openai import AsyncOpenAI


async def main():
    # Get credentials from environment variables
    metorial_api_key = os.getenv('METORIAL_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    deployment_id = os.getenv('METORIAL_DEPLOYMENT_ID')
    
    if not all([metorial_api_key, openai_api_key, deployment_id]):
        print("Error: Missing environment variables!")
        print("Please set: METORIAL_API_KEY, OPENAI_API_KEY, METORIAL_DEPLOYMENT_ID")
        return
    
    # Initialize clients
    metorial = Metorial(api_key=metorial_api_key)
    openai = AsyncOpenAI(api_key=openai_api_key)
    
    # Run query
    response = await metorial.run(
        message="Search Hackernews for the latest AI discussions.",
        server_deployments=[deployment_id],
        client=openai,
        model="gpt-4o",
        max_steps=25
    )
    
    print("Response:", response.text)


if __name__ == "__main__":
    asyncio.run(main())
'''


def use_metorial():
    """Add Metorial MCP integration to the project."""
    
    # Check if we're in a FastApps project
    if not Path("server").exists():
        console.print("[red]Error: Not in a FastApps project directory.[/red]")
        console.print("[yellow]Please run this command from your project root.[/yellow]")
        console.print("\n[cyan]If you haven't initialized a project yet:[/cyan]")
        console.print("  fastapps init myproject")
        return False
    
    # Create api directory if it doesn't exist
    api_dir = Path("server/api")
    api_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py in api directory
    init_file = api_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")
    
    # Create metorial_mcp.py file
    metorial_file = api_dir / "metorial_mcp.py"
    
    if metorial_file.exists():
        console.print(f"[yellow]Warning: {metorial_file} already exists.[/yellow]")
        console.print("[yellow]Skipping file creation.[/yellow]")
    else:
        metorial_file.write_text(METORIAL_TEMPLATE)
        console.print(f"\n[green]✓ Created: {metorial_file}[/green]")
    
    # Check requirements.txt and suggest adding dependencies
    req_file = Path("requirements.txt")
    if req_file.exists():
        requirements = req_file.read_text()
        needs_metorial = "metorial" not in requirements
        needs_openai = "openai" not in requirements
        
        if needs_metorial or needs_openai:
            console.print("\n[yellow]⚠ Missing dependencies in requirements.txt:[/yellow]")
            if needs_metorial:
                console.print("  - metorial")
            if needs_openai:
                console.print("  - openai")
            
            console.print("\n[cyan]Add these dependencies:[/cyan]")
            console.print("  echo 'metorial' >> requirements.txt")
            console.print("  echo 'openai' >> requirements.txt")
            console.print("  pip install -r requirements.txt")
    
    # Display setup instructions
    console.print("\n[bold green]✓ Metorial MCP integration added![/bold green]")
    console.print("\n[cyan]Setup Instructions:[/cyan]")
    console.print("\n[yellow]1. Install dependencies:[/yellow]")
    console.print("   pip install metorial openai")
    
    console.print("\n[yellow]2. Set environment variables:[/yellow]")
    console.print("   export METORIAL_API_KEY='your_metorial_api_key'")
    console.print("   export OPENAI_API_KEY='your_openai_api_key'")
    console.print("   export METORIAL_DEPLOYMENT_ID='your_deployment_id'")
    
    console.print("\n[yellow]3. Test the integration:[/yellow]")
    console.print("   python server/api/metorial_mcp.py")
    console.print("\n[yellow]4. Customize the query:[/yellow]")
    console.print("   Edit server/api/metorial_mcp.py to change the message or model")
    
    console.print("\n[dim]Documentation: https://metorial.ai/docs[/dim]")
    console.print()
    
    return True


def use_integration(integration_name: str):
    """
    Add an integration to the FastApps project.
    
    Args:
        integration_name: Name of the integration (e.g., 'metorial')
    """
    
    if integration_name == "metorial":
        return use_metorial()
    else:
        console.print(f"[red]Error: Unknown integration '{integration_name}'[/red]")
        console.print("\n[cyan]Available integrations:[/cyan]")
        console.print("  - metorial    Add Metorial MCP integration")
        console.print("\n[dim]More integrations coming soon![/dim]")
        return False

