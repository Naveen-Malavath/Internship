"""Main CLI entry point for the AI Coding Agent"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.core.config import get_config
from src.core.orchestrator import CodingAgent
from src.utils.logger import setup_logger

app = typer.Typer(
    name="coding-agent",
    help="AI Coding Agent - Generate full-stack apps from a single prompt",
    add_completion=False,
)
console = Console()


@app.command()
def run(
    prompt: str = typer.Argument(..., help="Task description for the agent"),
    workspace: Optional[str] = typer.Option(
        None, "--workspace", "-w", help="Workspace directory"
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="LLM provider (openai or anthropic)"
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
):
    """
    Run the coding agent with a prompt
    
    Example:
        coding-agent run "Create a todo app with React and Express"
    """
    # Setup logging
    log_level = "DEBUG" if debug else "INFO"
    setup_logger(log_level)

    # Display welcome banner
    console.print(
        Panel.fit(
            "[bold cyan]AI Coding Agent[/bold cyan]\n[dim]Autonomous Full-Stack Development[/dim]",
            border_style="cyan",
        )
    )

    # Parse workspace
    workspace_path = Path(workspace) if workspace else Path.cwd()

    # Display task
    console.print(f"\n[bold green]Task:[/bold green] {prompt}")
    console.print(f"[dim]Workspace:[/dim] {workspace_path}\n")

    # Create agent and run
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Agent working...", total=None)

            # Run async agent
            result = asyncio.run(_run_agent(prompt, workspace_path, provider, model))

            progress.update(task, completed=True)

        # Display results
        if result["success"]:
            console.print("\n[bold green]✓ Task completed successfully![/bold green]")
            console.print(f"[dim]Iterations: {result['iterations']}[/dim]\n")

            if result["response"]:
                console.print(Panel(result["response"], title="Agent Response", border_style="green"))
        else:
            console.print("\n[bold red]✗ Task failed[/bold red]")
            console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Agent interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if debug:
            import traceback
            console.print(traceback.format_exc())


async def _run_agent(
    prompt: str,
    workspace_path: Path,
    provider: Optional[str],
    model: Optional[str],
):
    """Helper to run agent asynchronously"""
    agent = CodingAgent(
        workspace_path=workspace_path,
        llm_provider=provider,
        model=model,
    )
    return await agent.run(prompt)


@app.command()
def interactive(
    workspace: Optional[str] = typer.Option(
        None, "--workspace", "-w", help="Workspace directory"
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="LLM provider"
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name"),
):
    """
    Start interactive chat session with the agent
    """
    setup_logger("INFO")

    console.print(
        Panel.fit(
            "[bold cyan]AI Coding Agent - Interactive Mode[/bold cyan]\n[dim]Type 'exit' to quit[/dim]",
            border_style="cyan",
        )
    )

    workspace_path = Path(workspace) if workspace else Path.cwd()
    agent = CodingAgent(workspace_path=workspace_path, llm_provider=provider, model=model)

    while True:
        try:
            user_input = console.input("\n[bold cyan]You:[/bold cyan] ")

            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if not user_input.strip():
                continue

            # Run agent
            result = asyncio.run(agent.run(user_input))

            if result["success"] and result["response"]:
                console.print(f"\n[bold green]Agent:[/bold green] {result['response']}")
            elif not result["success"]:
                console.print(f"[red]Error: {result.get('error')}[/red]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def version():
    """Show version information"""
    from src import __version__

    console.print(f"[cyan]AI Coding Agent[/cyan] version [bold]{__version__}[/bold]")


@app.command()
def config():
    """Show current configuration"""
    cfg = get_config()

    console.print(Panel("[bold]Current Configuration[/bold]", border_style="cyan"))
    console.print(f"Provider: {cfg.default_llm_provider}")
    console.print(f"OpenAI Model: {cfg.openai_model}")
    console.print(f"Anthropic Model: {cfg.anthropic_model}")
    console.print(f"Max Retries: {cfg.max_retries}")
    console.print(f"Timeout: {cfg.timeout_seconds}s")
    console.print(f"Log Level: {cfg.log_level}")


if __name__ == "__main__":
    app()
