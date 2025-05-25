# GitHub Cleaner

[![PyPI version](https://img.shields.io/pypi/v/github-cleaner.svg)](https://pypi.org/project/github-cleaner/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python package](https://github.com/RumTumTum/github-cleaner/actions/workflows/python-package.yml/badge.svg)](https://github.com/RumTumTum/github-cleaner/actions/workflows/python-package.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

🧹 **GitHub Cleaner** - A powerful Python CLI tool for GitHub repository management

Streamline your GitHub workflow with batch operations, smart filtering, and safe repository management. Perfect for developers, organizations, and anyone looking to organize their GitHub repositories efficiently.

**Key Benefits:**
- 🔍 **Smart Discovery**: View and filter repositories (yours or any public repos)
- 📊 **Batch Operations**: Export, archive, and delete multiple repositories safely
- 🛡️ **Safety First**: Preview operations, confirmation prompts, and detailed reporting
- 🚀 **Zero Setup**: Works immediately after `pip install` with minimal configuration
- 🎯 **Precision Control**: Advanced filtering by status, visibility, and ownership

## Package Structure

```
github_cleaner/
├── __init__.py      # Package initialization and version exports
├── __version__.py   # Version management
├── cli.py          # Click-based command-line interface
└── core.py         # Core GitHub operations and utilities
```

The package is structured as a proper Python package with:
- **Modular design**: Separation of CLI logic from core functionality
- **Entry point**: `github-cleaner` command available after installation
- **Version management**: Centralized version handling for PyPI releases
- **Clean imports**: Well-defined module boundaries and imports

## ✨ Features

### 🎯 Core Capabilities

- **📋 Repository Discovery & Listing**
  - List all your repositories with rich details (name, visibility, status, description)
  - View any user's public repositories without authentication
  - Advanced filtering by status (all, active, archived)
  - Beautiful tabular output with smart formatting

- **📤 Smart Export System**
  - Export repository lists to text files for batch processing
  - Full `owner/repo` format for seamless API integration
  - Filter exports by repository status
  - Works with both personal and public repository discovery

- **🔧 Safe Repository Management**
  - Batch archive and delete operations with safety controls
  - Interactive preview tables before any destructive operations
  - Required user confirmation with detailed operation summaries
  - Granular success/failure reporting for each repository
  - Built-in safeguards prevent accidental data loss

### Coming Soon

- **Single Repository Management**: Archive or delete individual repositories via CLI arguments

## 🚀 Quick Start

```bash
# Install from PyPI
pip install github-cleaner

# Set your GitHub token
export GITHUB_TOKEN=your_token_here

# List your repositories
github-cleaner list

# Export repository names for batch operations
github-cleaner list --export my-repos.txt
```

## Installation

### Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token (for private repos and management operations)

### Install from PyPI (Recommended)

```bash
pip install github-cleaner
```

That's it! The `github-cleaner` command will be available immediately.

### Alternative Installation Methods

<details>
<summary>🔧 Development Installation</summary>

```bash
# Clone the repository
git clone https://github.com/RumTumTum/github-cleaner.git
cd github-cleaner

# Install in development mode
pip install -e .
```
</details>

<details>
<summary>📦 Install from Source</summary>

```bash
# Clone the repository
git clone https://github.com/RumTumTum/github-cleaner.git
cd github-cleaner

# Install dependencies
pip install -r requirements.txt
```
</details>

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

### Viewing Your Repositories

```bash
# List all repositories
github-cleaner list

# List only active (non-archived) repositories
github-cleaner list --filter active

# List only archived repositories
github-cleaner list --filter archived

# Show full repository names (owner/repo format)
github-cleaner list --full-names

# Combine filters with full names
github-cleaner list --filter active --full-names
```

### Viewing Public Repositories (No Token Required)

```bash
# View all public repositories for a user
github-cleaner public username

# View only active public repositories for a user
github-cleaner public username --filter active

# View only archived public repositories for a user
github-cleaner public username --filter archived

# Show full repository names (owner/repo format)
github-cleaner public username --full-names

# Combine filters with full names
github-cleaner public username --filter active --full-names
```

### Exporting Repository Lists

Export repository names to text files for further processing. All exports use the full `owner/repo` format regardless of display options.

```bash
# Export all your repositories
github-cleaner list --export my-repos.txt

# Export only active repositories
github-cleaner list --filter active --export active-repos.txt

# Export only archived repositories  
github-cleaner list --filter archived --export archived-repos.txt

# Export all public repositories for a user
github-cleaner public octocat --export octocat-repos.txt

# Export only active public repositories for a user
github-cleaner public octocat --filter active --export octocat-active.txt

# Note: --full-names flag doesn't affect export format
github-cleaner list --full-names --export repos.txt  # Still exports owner/repo format
```

**Export File Format:**
```
owner/repository-name-1
owner/repository-name-2
owner/repository-name-3
```

### Managing Repositories (Archive/Delete)

Perform batch operations on your repositories using exported lists. **Requires authentication and only works with your own repositories.**

```bash
# First, export repositories to manage
github-cleaner list --filter archived --export old-repos.txt

# Archive repositories (reversible)
github-cleaner manage old-repos.txt archive

# Delete repositories (IRREVERSIBLE - use with caution!)
github-cleaner manage unwanted-repos.txt delete

# You can also manage repositories from any exported list
github-cleaner list --export all-repos.txt
github-cleaner manage all-repos.txt archive
```

**⚠️ Important Safety Notes:**
- **Preview Required**: Always shows preview table before execution
- **User Confirmation**: Must explicitly type 'yes' to proceed
- **Delete Warning**: Extra warnings for irreversible delete operations
- **One-by-One Processing**: Failed repositories don't stop the entire operation
- **Your Repos Only**: Only works with repositories you own or have admin access to

**File Format**: Use the same format as export output (`owner/repo` per line):
```
username/repo-to-archive
username/repo-to-delete
username/another-repo
```

### Help

```bash
# Display help for all commands
github-cleaner --help

# Display help for a specific command
github-cleaner list --help
github-cleaner public --help
github-cleaner manage --help
```

## Examples

### Viewing all repositories

```bash
$ github-cleaner list
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

### Viewing someone's public repositories

```bash
$ github-cleaner public octocat --filter active
                    Active Public Repositories for @octocat                     
┌────────────────────┬────────────┬────────┬───────────────────────────────────┐
│ Name               │ Visibility │ Status │ Description                       │
├────────────────────┼────────────┼────────┼───────────────────────────────────┤
│ boysenberry-repo-1 │ Public     │ Active │ Testing                           │
│ git-consortium     │ Public     │ Active │ This repo is for demonstration    │
│                    │            │        │ purposes only.                    │
│ hello-worId        │ Public     │ Active │ My first repository on GitHub.    │
│ Hello-World        │ Public     │ Active │ My first repository on GitHub!    │
│ linguist           │ Public     │ Active │ Language Savant. If your          │
│                    │            │        │ repository language is being      │
│                    │            │        │ reported incorrectly, send us a   │
│                    │            │        │ pull request!                     │
│ octocat.github.io  │ Public     │ Active │                                   │
│ Spoon-Knife        │ Public     │ Active │ This repo is for demonstration    │
│                    │            │        │ purposes only.                    │
│ test-repo1         │ Public     │ Active │                                   │
└────────────────────┴────────────┴────────┴───────────────────────────────────┘

Total active public repositories: 8
```

### Exporting repository lists

```bash
$ github-cleaner public octocat --filter active --export octocat-repos.txt
Success: Exported 8 active public repositories for @octocat to octocat-repos.txt

$ cat octocat-repos.txt
octocat/boysenberry-repo-1
octocat/git-consortium
octocat/hello-worId
octocat/Hello-World
octocat/linguist
octocat/octocat.github.io
octocat/Spoon-Knife
octocat/test-repo1
```

### Displaying full repository names

Compare the difference between default display and full names display:

```bash
# Default display (just repository names)
$ github-cleaner public octocat --filter active
                    Active Public Repositories for @octocat                     
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name               ┃ Visibility ┃ Status ┃ Description                       ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ boysenberry-repo-1 │ Public     │ Active │ Testing                           │
│ Hello-World        │ Public     │ Active │ My first repository on GitHub!    │
└────────────────────┴────────────┴────────┴───────────────────────────────────┘

# Full names display (owner/repo format)
$ github-cleaner public octocat --filter active --full-names
                    Active Public Repositories for @octocat                     
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                       ┃ Visibility ┃ Status ┃ Description               ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ octocat/boysenberry-repo-1 │ Public     │ Active │ Testing                   │
│ octocat/Hello-World        │ Public     │ Active │ My first repository on    │
│                            │            │        │ GitHub!                   │
└────────────────────────────┴────────────┴────────┴───────────────────────────┘
```

### Managing repositories with preview and confirmation

Complete workflow showing archive operation with safety features:

```bash
# Step 1: Export repositories to manage
$ github-cleaner list --filter archived --export archived-repos.txt
Success: Exported 5 archived repositories to archived-repos.txt

# Step 2: Review the file contents
$ cat archived-repos.txt
username/old-project-1
username/legacy-code
username/deprecated-tool
username/test-repository
username/archived-demo

# Step 3: Run manage command with preview
$ github-cleaner manage archived-repos.txt archive
Found 5 repositories in archived-repos.txt
                   Planned Operation: ARCHIVE                    
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Repository            ┃ Current Status ┃ Planned Action       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ username/old-project-1│ Active         │ ARCHIVE (reversible) │
│ username/legacy-code  │ Active         │ ARCHIVE (reversible) │
│ username/deprecated-tool│ Archived     │ ARCHIVE (reversible) │
│ username/test-repository│ Active       │ ARCHIVE (reversible) │
│ username/archived-demo│ Archived       │ ARCHIVE (reversible) │
└───────────────────────┴────────────────┴──────────────────────┘

WARNING: You are about to ARCHIVE 5 repositories.

Type 'yes' to archive these repositories, or 'no' to cancel: yes

Starting archive operations...
[1/5] Processing username/old-project-1...
  ✓ Already archived
[2/5] Processing username/legacy-code...
  ✓ Successfully archived
[3/5] Processing username/deprecated-tool...
  ✗ Repository not found or no access
[4/5] Processing username/test-repository...
  ✓ Successfully archived
[5/5] Processing username/archived-demo...
  ✓ Already archived

Operation Summary:
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Repository                ┃ Operation ┃ Status  ┃ Details                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ username/old-project-1    │ ARCHIVE   │ SUCCESS │ Already archived                 │
│ username/legacy-code      │ ARCHIVE   │ SUCCESS │ Successfully archived           │
│ username/deprecated-tool  │ ARCHIVE   │ FAILED  │ Repository not found or no access│
│ username/test-repository  │ ARCHIVE   │ SUCCESS │ Successfully archived           │
│ username/archived-demo    │ ARCHIVE   │ SUCCESS │ Already archived                 │
└───────────────────────────┴───────────┴─────────┴──────────────────────────────────┘

Results: 4 successful, 1 failed
Some operations failed. Check the details above for more information.
```

## Development

### Setting up a development environment

```bash
# Clone the repository
git clone https://github.com/RumTumTum/github-cleaner.git
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

# Verify installation
github-cleaner --help
```

### Running tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test files
pytest tests/test_list_repos.py      # Tests for authenticated repository listing
pytest tests/test_public_repos.py   # Tests for public repository discovery
pytest tests/test_export_repos.py   # Tests for export functionality (--export flag)
pytest tests/test_full_names.py     # Tests for full names display (--full-names flag)
pytest tests/test_manage.py         # Tests for repository management (archive/delete)

# Run with coverage report (requires pytest-cov)
pytest --cov=github_cleaner

# Run linting on the package
flake8 github_cleaner

# Run type checking on the package
mypy github_cleaner
```

### Test Coverage

The test suite covers:
- **Authenticated Operations**: Repository listing with filtering (all, active, archived)
- **Public Repository Discovery**: Unauthenticated access to any user's public repos
- **Repository Export**: Export functionality via `--export` flag for both list and public commands
- **Repository Management**: Archive and delete operations with comprehensive safety testing
- **Display Options**: Full names display via `--full-names` flag for both list and public commands
- **File Operations**: Export file creation, repository list reading, permission error handling
- **Data Format Validation**: Ensuring full repository names (`owner/repo`) in export and manage files
- **UI/Display Testing**: Verification of table output formats and content display
- **Safety Features**: User confirmation, preview tables, operation results reporting
- **Flag Combinations**: Testing interactions between filters, export, and display options
- **Error Handling**: GitHub API errors, user not found, network issues, file system errors, permission issues
- **Edge Cases**: Empty repository lists, various filter combinations, mixed repository types, failed operations

## Continuous Integration

This project uses GitHub Actions for automated testing and quality assurance.

### CI/CD Pipeline

- **Workflow**: Runs on Python 3.9, 3.10, and 3.11
- **Triggers**: 
  - Push to `main` or `dev` branches
  - Pull requests targeting `main` or `dev` branches
- **Steps**:
  1. **Dependency Installation**: Install project and test dependencies
  2. **Linting**: Code quality checks with flake8
  3. **Testing**: Full test suite execution with pytest

### Branch Protection

Both `main` and `dev` branches are protected with the following requirements:

1. **Status Checks**: All CI tests must pass before merging
2. **Required Reviews**: Pull request reviews required
3. **No Direct Pushes**: Changes must come through pull requests
4. **Up-to-date Branches**: Branches must be up-to-date before merging

**Setting up Branch Protection (Repository Admin)**:

1. Go to **Settings** → **Branches** in your GitHub repository
2. Add protection rules for `main` and `dev` branches:
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
   - ✅ **Select specific status checks** (critical for preventing queued merges):
     - `All Tests Complete` (summary job that ensures all tests pass)
     - `Test Python 3.9` (individual test jobs)
     - `Test Python 3.10`
     - `Test Python 3.11`
   - ✅ **Require pull request reviews before merging**
   - ✅ **Dismiss stale reviews when new commits are pushed**
   - ✅ **Do not allow bypassing the above settings**
   - ✅ **Restrict pushes that create files larger than 100MB**

**🔑 Key Fix**: Select **specific status checks** rather than just the general "Python package" workflow. This prevents merging while checks are queued/running.

## Publishing to PyPI

### Prerequisites for Publishing

- Ensure you have `build` and `twine` installed:
  ```bash
  pip install build twine
  ```
- Create accounts on [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org)
- Configure your API tokens for secure uploads

### Build and Publish Process

```bash
# 1. Update version in github_cleaner/__version__.py
# 2. Clean previous builds
rm -rf dist/ build/ *.egg-info/

# 3. Build the package
python -m build

# 4. Check the build
twine check dist/*

# 5. Upload to TestPyPI first (recommended)
twine upload --repository testpypi dist/*

# 6. Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ github-cleaner

# 7. If everything works, upload to PyPI
twine upload dist/*
```

### Version Management

Update the version in `github_cleaner/__version__.py` before each release:
```python
__version__ = "0.2.0"  # Update this for new releases
```

The version is automatically read by `setup.py` during the build process.

## Contributing

Contributions are welcome! Please follow our development workflow:

### Development Workflow

1. **Fork the repository**
2. **Create your feature branch** from `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes** and ensure tests pass:
   ```bash
   pytest
   flake8 .
   ```
4. **Commit your changes** with descriptive messages:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request** targeting the `dev` branch

### Pull Request Guidelines

- **Target Branch**: Always target `dev` branch for new features
- **Tests Required**: All tests must pass (CI will verify this)
- **Code Quality**: Must pass linting checks
- **Description**: Provide clear description of changes
- **Small PRs**: Keep pull requests focused and reasonably sized

### Release Process

- **Feature Development**: `feature/xyz` → `dev` → merge after CI passes
- **Releases**: `dev` → `main` → create release tag
- **Hotfixes**: `hotfix/xyz` → `main` → backport to `dev`

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