# github-cleaner

A Python CLI tool to clean and manage GitHub repositories.

## Planned Capabilities

1. **View Repositories**: Display all repositories with relevant information
   - Filter by status (all, active, archived)
   - Show key repository details

2. **Export Repository List**: Generate a text file of repository names
   - Filter by status (all, active, archived)
   - One repository name per line

3. **Archive/Delete Single Repository**: Manage repositories via CLI
   - Archive or delete a repository by name
   - Confirmation before permanent actions

4. **Batch Archive/Delete Repositories**: Process multiple repositories
   - Read repository names from a text file
   - Perform archive or delete actions on all listed repositories

## Authentication

To use this tool, you'll need to provide GitHub credentials:

1. Personal Access Token (recommended):
   - Create a token at GitHub (Settings → Developer Settings → Personal Access Tokens)
   - Set the token as an environment variable: `export GITHUB_TOKEN=your_token_here`

2. Alternative authentication methods will be documented as implemented