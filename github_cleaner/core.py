"""Core GitHub operations and utility functions."""

import os
import sys
from typing import List, Optional

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


def get_repository_status(github_client: Github, repo_name: str) -> str:
    """Get the current status of a repository."""
    try:
        repo = github_client.get_repo(repo_name)
        if repo.archived:
            return "Already Archived"
        else:
            return "Active"
    except GithubException as e:
        if "Not Found" in str(e):
            return "Not Found"
        elif "permission" in str(e).lower() or "403" in str(e):
            return "No Permission"
        else:
            return "Error"
    except Exception:
        return "Unknown"


def create_operation_preview_table(repo_statuses: List[dict], operation: str) -> Table:
    """Create a table showing the planned operations on repositories."""
    table = Table(title=f"Planned Operation: {operation.upper()}")
    table.add_column("Repository", style="cyan")
    table.add_column("Current Status", style="yellow")
    table.add_column("Planned Action", style="red" if operation == "delete" else "magenta")
    
    for repo_info in repo_statuses:
        repo_name = repo_info["name"]
        status = repo_info["status"]
        
        # Determine planned action based on current status
        if operation == "delete":
            if status in ["Not Found", "No Permission", "Error"]:
                action_desc = "CANNOT DELETE"
            else:
                action_desc = "DELETE (irreversible)"
        else:  # archive
            if status == "Already Archived":
                action_desc = "NO CHANGE NEEDED"
            elif status in ["Not Found", "No Permission", "Error"]:
                action_desc = "CANNOT ARCHIVE"
            else:
                action_desc = "ARCHIVE (reversible)"
        
        # Color code the status
        if status in ["Not Found", "No Permission", "Error"]:
            status_display = f"[red]{status}[/red]"
        elif status == "Already Archived":
            status_display = f"[dim]{status}[/dim]"
        else:
            status_display = f"[green]{status}[/green]"
        
        table.add_row(repo_name, status_display, action_desc)
    
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