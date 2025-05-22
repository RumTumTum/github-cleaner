#!/usr/bin/env python3

import os
import sys
from typing import Optional

import click
from github import Github, GithubException
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
    token = get_github_token()
    
    try:
        # Initialize GitHub client
        g = Github(token)
        user = g.get_user()
        
        # Get repositories based on filter
        if repo_filter == "all":
            repos = user.get_repos()
            filter_desc = "All"
        elif repo_filter == "active":
            repos = [repo for repo in user.get_repos() if not repo.archived]
            filter_desc = "Active"
        else:  # archived
            repos = [repo for repo in user.get_repos() if repo.archived]
            filter_desc = "Archived"
        
        # Create and populate table
        table = Table(title=f"{filter_desc} GitHub Repositories")
        table.add_column("Name", style="cyan")
        table.add_column("Visibility", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Description")
        
        for repo in repos:
            status = "Archived" if repo.archived else "Active"
            visibility = "Private" if repo.private else "Public"
            description = repo.description or ""
            table.add_row(repo.name, visibility, status, description)
        
        # Count the repositories
        repo_count = sum(1 for _ in repos)
        
        # Display the table
        console.print(table)
        console.print(f"\nTotal repositories: {repo_count}")
        
    except GithubException as e:
        console.print(f"[bold red]GitHub Error:[/] {e}")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")


if __name__ == "__main__":
    cli()
