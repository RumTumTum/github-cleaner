"""Command-line interface for GitHub Cleaner."""

from typing import Optional

import click
from github import GithubException
from rich.console import Console

from .core import (
    create_operation_preview_table,
    create_operation_results_table,
    create_repository_table,
    confirm_operation,
    export_repositories,
    fetch_public_repositories,
    fetch_repositories,
    filter_repositories,
    get_repository_status,
    init_github_client,
    init_github_client_public,
    perform_repository_operation,
    read_repository_list,
)

# Initialize rich console for better output formatting
console = Console()


@click.group()
def cli():
    """GitHub Cleaner - A tool to manage GitHub repositories."""
    pass


@cli.command()
@click.option(
    "--filter",
    "repo_filter",
    type=click.Choice(["all", "active", "archived"]),
    default="all",
    help="Filter repositories by status",
)
@click.option(
    "--export",
    "-e",
    "export_file",
    help="Export repository names to specified file",
)
@click.option(
    "--full-names",
    is_flag=True,
    help="Display full repository names (owner/repo) in table output",
)
def list(repo_filter: str, export_file: Optional[str], full_names: bool):
    """List GitHub repositories based on filter criteria."""
    try:
        # Initialize GitHub client
        g = init_github_client()
        
        # Fetch all repositories
        all_repos = fetch_repositories(g)
        
        # Filter repositories based on criteria
        filtered_repos = filter_repositories(all_repos, repo_filter)
        
        # Get filter description
        filter_desc = repo_filter.capitalize() if repo_filter != "all" else "All"
        
        # Export to file if requested
        if export_file:
            export_repositories(filtered_repos, export_file)
            console.print(f"[green]Success:[/] Exported {len(filtered_repos)} {filter_desc.lower()} repositories to {export_file}")
        else:
            # Create and display table
            table = create_repository_table(filtered_repos, filter_desc, username=None, full_names=full_names)
            console.print(table)
            console.print(f"\nTotal repositories: {len(filtered_repos)}")
        
    except GithubException as e:
        console.print(f"[bold red]GitHub Error:[/] {e}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")


@cli.command()
@click.argument("username")
@click.option(
    "--filter",
    "repo_filter",
    type=click.Choice(["all", "active", "archived"]),
    default="all",
    help="Filter repositories by status",
)
@click.option(
    "--export",
    "-e",
    "export_file",
    help="Export repository names to specified file",
)
@click.option(
    "--full-names",
    is_flag=True,
    help="Display full repository names (owner/repo) in table output",
)
def public(username: str, repo_filter: str, export_file: Optional[str], full_names: bool):
    """View public repositories for any GitHub user."""
    try:
        # Initialize GitHub client without authentication
        g = init_github_client_public()
        
        # Fetch public repositories
        all_repos = fetch_public_repositories(g, username)
        
        # Filter repositories based on criteria
        filtered_repos = filter_repositories(all_repos, repo_filter)
        
        # Get filter description
        filter_desc = repo_filter.capitalize() if repo_filter != "all" else "All"
        
        # Export to file if requested
        if export_file:
            export_repositories(filtered_repos, export_file)
            console.print(f"[green]Success:[/] Exported {len(filtered_repos)} {filter_desc.lower()} public repositories for @{username} to {export_file}")
        else:
            # Create and display table
            table = create_repository_table(filtered_repos, filter_desc, username, full_names)
            console.print(table)
            console.print(f"\nTotal public repositories: {len(filtered_repos)}")
        
    except GithubException as e:
        if "Not Found" in str(e):
            console.print(f"[bold red]Error:[/] User '{username}' not found.")
        else:
            console.print(f"[bold red]GitHub Error:[/] {e}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("operation", type=click.Choice(["archive", "delete"]))
def manage(file_path: str, operation: str):
    """Manage repositories by performing archive or delete operations.
    
    FILE_PATH: Path to text file containing repository names (owner/repo format)
    OPERATION: Operation to perform (archive or delete)
    """
    try:
        # Read repository list from file
        repo_names = read_repository_list(file_path)
        
        if not repo_names:
            console.print("[bold red]Error:[/] No repositories found in the file.")
            return
        
        console.print(f"Found {len(repo_names)} repositories in {file_path}")
        
        # Check repository statuses
        console.print(f"\n[bold]Checking repository statuses...[/]")
        g = init_github_client()
        
        repo_statuses = []
        for i, repo_name in enumerate(repo_names, 1):
            console.print(f"[{i}/{len(repo_names)}] Checking {repo_name}...", end="")
            status = get_repository_status(g, repo_name)
            repo_statuses.append({"name": repo_name, "status": status})
            console.print(f" {status}")
        
        # Show preview table
        preview_table = create_operation_preview_table(repo_statuses, operation)
        console.print("\n")
        console.print(preview_table)
        
        # Count actionable repositories
        actionable_repos = []
        for repo_info in repo_statuses:
            status = repo_info["status"]
            if operation == "archive":
                if status not in ["Already Archived", "Not Found", "No Permission", "Error"]:
                    actionable_repos.append(repo_info["name"])
            else:  # delete
                if status not in ["Not Found", "No Permission", "Error"]:
                    actionable_repos.append(repo_info["name"])
        
        if not actionable_repos:
            console.print(f"[yellow]No repositories can be {operation}d. All repositories are either already processed or inaccessible.[/]")
            return
        
        if len(actionable_repos) < len(repo_names):
            skipped = len(repo_names) - len(actionable_repos)
            console.print(f"[yellow]Note: {skipped} repositories will be skipped due to status or permissions.[/]")
        
        # Ask for confirmation
        if not confirm_operation(operation, len(actionable_repos)):
            console.print("[yellow]Operation cancelled.[/]")
            return
        
        # Perform operations
        console.print(f"\n[bold]Starting {operation} operations...[/]")
        results = []
        
        for i, repo_name in enumerate(repo_names, 1):
            console.print(f"[{i}/{len(repo_names)}] Processing {repo_name}...")
            result = perform_repository_operation(g, repo_name, operation)
            results.append(result)
            
            # Show immediate feedback
            if result["success"]:
                console.print(f"  [green]✓[/] {result['details']}")
            else:
                console.print(f"  [red]✗[/] {result['details']}")
        
        # Show final results table
        console.print("\n[bold]Operation Summary:[/]")
        results_table = create_operation_results_table(results)
        console.print(results_table)
        
        # Summary statistics
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        console.print(f"\n[bold]Results:[/] {successful} successful, {failed} failed")
        
        if failed > 0:
            console.print("[yellow]Some operations failed. Check the details above for more information.[/]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")


if __name__ == "__main__":
    cli()