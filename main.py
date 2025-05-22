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


def create_repository_table(repos: List[Repository], filter_desc: str, username: Optional[str] = None) -> Table:
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
        table.add_row(repo.name, visibility, status, description)
    
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
def list(repo_filter: str):
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
        
        # Create and display table
        table = create_repository_table(filtered_repos, filter_desc)
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
def public(username: str, repo_filter: str):
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
        
        # Create and display table
        table = create_repository_table(filtered_repos, filter_desc, username)
        console.print(table)
        console.print(f"\nTotal public repositories: {len(filtered_repos)}")
        
    except GithubException as e:
        if "Not Found" in str(e):
            console.print(f"[bold red]Error:[/] User '{username}' not found.")
        else:
            console.print(f"[bold red]GitHub Error:[/] {e}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")


if __name__ == "__main__":
    cli()
