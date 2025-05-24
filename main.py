#!/usr/bin/env python3

import os
import sys
from typing import List, Optional

import click
from github import Github, GithubException
from github.Repository import Repository
from rich.console import Console
from rich.table import Table

# Initialize rich console for better output formatting
console = Console()


def get_github_token() -> str:
    """Get GitHub token from environment variable."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        console.print(
            "[bold red]Error:[/] GitHub token not found. Please set the GITHUB_TOKEN environment variable."
        )
        console.print("Example: export GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    return token


def init_github_client() -> Github:
    """Initialize and return GitHub client."""
    token = get_github_token()
    return Github(token)


def init_github_client_public() -> Github:
    """Initialize and return GitHub client for public access (no authentication)."""
    return Github()


def fetch_repositories(github_client: Github) -> List[Repository]:
    """Fetch all repositories for the authenticated user."""
    user = github_client.get_user()
    # Convert PaginatedList to list by iterating (avoid direct list() conversion)
    # Note: Using list(repos) causes "object of type 'Repository' has no len()" error
    repos = user.get_repos()
    repos_list = []
    for repo in repos:
        repos_list.append(repo)
    return repos_list


def fetch_public_repositories(github_client: Github, username: str) -> List[Repository]:
    """Fetch public repositories for any GitHub user by username."""
    user = github_client.get_user(username)
    # Get only public repositories
    repos = user.get_repos(type='public')
    repos_list = []
    for repo in repos:
        repos_list.append(repo)
    return repos_list


def filter_repositories(repos: List[Repository], filter_type: str) -> List[Repository]:
    """Filter repositories based on the specified criteria."""
    if filter_type == "all":
        return repos
    elif filter_type == "active":
        return [repo for repo in repos if not repo.archived]
    elif filter_type == "archived":
        return [repo for repo in repos if repo.archived]
    else:
        raise ValueError(f"Invalid filter type: {filter_type}")


def export_repositories(repos: List[Repository], output_file: str) -> None:
    """Export repository full names to a text file, one per line."""
    with open(output_file, 'w') as f:
        for repo in repos:
            f.write(f"{repo.full_name}\n")


def read_repository_list(file_path: str) -> List[str]:
    """Read repository names from a text file, one per line."""
    try:
        with open(file_path, 'r') as f:
            # Strip whitespace and filter out empty lines
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(f"Repository list file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading repository list file: {e}")


def create_operation_preview_table(repo_names: List[str], operation: str) -> Table:
    """Create a table showing the planned operations on repositories."""
    table = Table(title=f"Planned Operation: {operation.upper()}")
    table.add_column("Repository", style="cyan")
    table.add_column("Current Status", style="yellow")
    table.add_column("Planned Action", style="red" if operation == "delete" else "magenta")
    
    for repo_name in repo_names:
        action_desc = "DELETE (irreversible)" if operation == "delete" else "ARCHIVE (reversible)"
        table.add_row(repo_name, "Unknown", action_desc)
    
    return table


def create_operation_results_table(results: List[dict]) -> Table:
    """Create a table showing the results of repository operations."""
    table = Table(title="Operation Results")
    table.add_column("Repository", style="cyan")
    table.add_column("Operation", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    for result in results:
        status_style = "green" if result["success"] else "red"
        status_text = "SUCCESS" if result["success"] else "FAILED"
        table.add_row(
            result["repo_name"],
            result["operation"].upper(),
            f"[{status_style}]{status_text}[/{status_style}]",
            result["details"]
        )
    
    return table


def confirm_operation(operation: str, repo_count: int) -> bool:
    """Ask user to confirm the operation before proceeding."""
    action_desc = "DELETE (IRREVERSIBLE)" if operation == "delete" else "ARCHIVE"
    
    console.print(f"\n[bold red]WARNING:[/] You are about to {action_desc} {repo_count} repositories.")
    if operation == "delete":
        console.print("[bold red]DELETION IS IRREVERSIBLE - repositories cannot be recovered![/]")
    
    while True:
        response = input(f"\nType 'yes' to {operation} these repositories, or 'no' to cancel: ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n', '']:
            return False
        else:
            console.print("Please type 'yes' or 'no'")


def perform_repository_operation(github_client: Github, repo_name: str, operation: str) -> dict:
    """Perform archive or delete operation on a single repository."""
    try:
        repo = github_client.get_repo(repo_name)
        
        if operation == "archive":
            if repo.archived:
                return {
                    "repo_name": repo_name,
                    "operation": operation,
                    "success": True,
                    "details": "Already archived"
                }
            repo.edit(archived=True)
            return {
                "repo_name": repo_name,
                "operation": operation,
                "success": True,
                "details": "Successfully archived"
            }
        
        elif operation == "delete":
            repo.delete()
            return {
                "repo_name": repo_name,
                "operation": operation,
                "success": True,
                "details": "Successfully deleted"
            }
        
        else:
            return {
                "repo_name": repo_name,
                "operation": operation,
                "success": False,
                "details": f"Unknown operation: {operation}"
            }
    
    except GithubException as e:
        error_msg = str(e)
        if "Not Found" in error_msg:
            details = "Repository not found or no access"
        elif "permission" in error_msg.lower():
            details = "Insufficient permissions"
        else:
            details = f"GitHub error: {error_msg}"
        
        return {
            "repo_name": repo_name,
            "operation": operation,
            "success": False,
            "details": details
        }
    
    except Exception as e:
        return {
            "repo_name": repo_name,
            "operation": operation,
            "success": False,
            "details": f"Unexpected error: {str(e)}"
        }


def create_repository_table(repos: List[Repository], filter_desc: str, username: Optional[str] = None, full_names: bool = False) -> Table:
    """Create and populate a table with repository information."""
    if username:
        title = f"{filter_desc} Public Repositories for @{username}"
    else:
        title = f"{filter_desc} GitHub Repositories"
    
    table = Table(title=title)
    table.add_column("Name", style="cyan")
    table.add_column("Visibility", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Description")
    
    for repo in repos:
        status = "Archived" if repo.archived else "Active"
        visibility = "Private" if repo.private else "Public"
        description = repo.description or ""
        repo_name = repo.full_name if full_names else repo.name
        table.add_row(repo_name, visibility, status, description)
    
    return table


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
        
        # Show preview table
        preview_table = create_operation_preview_table(repo_names, operation)
        console.print(preview_table)
        
        # Ask for confirmation
        if not confirm_operation(operation, len(repo_names)):
            console.print("[yellow]Operation cancelled.[/]")
            return
        
        # Initialize GitHub client
        g = init_github_client()
        
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
