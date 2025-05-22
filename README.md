# GitHub Cleaner

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A Python CLI tool to manage GitHub repositories efficiently. Clean up your GitHub account by viewing, exporting, archiving, and deleting repositories with ease.

## Features

### Implemented

- **Repository Listing**: View all your repositories with filtering capabilities:
  - List all repositories with key information (name, visibility, status, description)
  - Filter by repository status (all, active, archived)
  - Clean, tabular output for easy reading

### Coming Soon

- **Repository Export**: Generate lists of repository names for further processing
- **Single Repository Management**: Archive or delete individual repositories via CLI
- **Batch Operations**: Process multiple repositories from a text file
- **Public Repository Discovery**: View any user's public repositories without authentication using just their GitHub handle

## Installation

### Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token with appropriate permissions

### Option 1: Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/github-cleaner.git
cd github-cleaner

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Development installation

```bash
# Clone the repository
git clone https://github.com/yourusername/github-cleaner.git
cd github-cleaner

# Install in development mode
pip install -e .
```

## Authentication

GitHub Cleaner requires authentication to access your repositories:

### Setting up a Personal Access Token (PAT)

#### Option 1: Fine-Grained Token (Recommended)

1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens > Fine-grained tokens](https://github.com/settings/tokens?type=beta)
2. Click "Generate new token"
3. Give it a descriptive name (e.g., "GitHub Cleaner")
4. Set the expiration date as appropriate
5. Select the resource owner (your username or organization)
6. Under "Repository access," select either:
   - "All repositories" for access to all your repositories
   - "Only select repositories" to limit access to specific repositories
7. Under "Permissions," select the following minimal permissions:
   - Repository permissions:
     - "Administration": Read and Write (for archive/delete operations)
     - "Contents": Read-only (to list repositories)
     - "Metadata": Read-only (required for all tokens)
8. Click "Generate token"
9. Copy the token and store it safely (you won't be able to see it again)

#### Option 2: Classic Token

1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token" (classic)
3. Give it a descriptive name
4. Select the following scopes:
   - `repo` (Full control of private repositories)
   - `delete_repo` (If you plan to use the delete feature)
5. Click "Generate token"
6. Copy the token and store it safely (you won't be able to see it again)

### Setting the token for GitHub Cleaner

```bash
# Set the token as an environment variable
export GITHUB_TOKEN=your_token_here

# For Windows Command Prompt
set GITHUB_TOKEN=your_token_here

# For Windows PowerShell
$env:GITHUB_TOKEN = "your_token_here"
```

For persistent storage, add the export command to your shell profile file (e.g., `.bashrc`, `.zshrc`).

## Usage

### Viewing Repositories

```bash
# List all repositories
python main.py list

# List only active (non-archived) repositories
python main.py list --filter active

# List only archived repositories
python main.py list --filter archived
```

### Help

```bash
# Display help for all commands
python main.py --help

# Display help for a specific command
python main.py list --help
```

## Examples

### Viewing all repositories

```bash
$ python main.py list
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                 All GitHub Repositories                                                                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Name                 │ Visibility │ Status   │ Description                                                                                             │
│ github-cleaner       │ Public     │ Active   │ A Python CLI tool to clean and manage GitHub repositories                                               │
│ awesome-project      │ Private    │ Active   │ My awesome project                                                                                      │
│ old-project          │ Public     │ Archived │ Legacy code from 2020                                                                                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

Total repositories: 3
```

## Development

### Setting up a development environment

```bash
# Clone the repository
git clone https://github.com/yourusername/github-cleaner.git
cd github-cleaner

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running tests

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest

# Run specific test file
pytest tests/test_list_repos.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=github_cleaner
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Known Issues and Solutions

### PyGithub PaginatedList Conversion Issue

**Problem**: When working with PyGithub's `PaginatedList` objects (returned by `user.get_repos()`), using `list(paginated_list)` can cause a `TypeError: object of type 'Repository' has no len()` error.

**Root Cause**: The `list()` constructor internally tries to optimize the conversion by checking if the object has a `__len__` method. During this process, it appears to call `len()` on individual Repository objects within the PaginatedList, which don't support the `len()` operation.

**Solution**: Instead of using `list(paginated_list)`, manually iterate through the PaginatedList:

```python
# ❌ This causes the error
repos_list = list(user.get_repos())

# ✅ This works correctly
repos = user.get_repos()
repos_list = []
for repo in repos:
    repos_list.append(repo)
```

**Alternative Solutions**:
```python
# Using list comprehension (also works)
repos_list = [repo for repo in user.get_repos()]

# Using itertools.chain (if you need to combine multiple PaginatedLists)
import itertools
repos_list = list(itertools.chain(user.get_repos()))
```

**Impact**: This issue affects any code that needs to:
- Get the count of repositories (`len()` operation)
- Convert PaginatedList to a regular Python list for processing
- Pass repository collections to functions expecting List[Repository]

**Testing**: This issue was discovered through debugging when the application threw `TypeError: object of type 'Repository' has no len()` despite no explicit `len()` calls on Repository objects in the codebase.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub API for Python
- [Click](https://click.palletsprojects.com/) - Command Line Interface toolkit
- [Rich](https://github.com/Textualize/rich) - Terminal formatting library