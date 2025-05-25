import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from click.testing import CliRunner

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from github_cleaner.cli import cli

# Create a mock for GitHub Repository objects
class MockRepository:
    def __init__(self, name, private=False, archived=False, description=""):
        self.name = name
        self.private = private
        self.archived = archived
        self.description = description
    
    def __str__(self):
        return self.name


class TestPublicRepositories(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
    
    @patch('github_cleaner.core.Github')
    def test_public_repos_all(self, mock_github):
        # Set up mock repos
        mock_repo1 = MockRepository(
            name='public-repo1',
            private=False,
            archived=False,
            description='Public repo 1'
        )
        
        mock_repo2 = MockRepository(
            name='public-repo2',
            private=False,
            archived=True,
            description='Archived public repo'
        )
        
        # Set up mock user and github (no authentication)
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the command
        result = self.runner.invoke(cli, ['public', 'testuser'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify GitHub was called without authentication
        mock_github.assert_called_once_with()
        
        # Verify get_user was called with the username
        mock_github.return_value.get_user.assert_called_once_with('testuser')
        
        # Verify get_repos was called with type='public'
        mock_user.get_repos.assert_called_once_with(type='public')
        
        # Check if the output contains the expected title with username
        self.assertIn('All Public Repositories for @testuser', result.output)
        
        # Check if both repository names are in the output
        self.assertIn('public-repo1', result.output)
        self.assertIn('public-repo2', result.output)
        
        # Check repository count (should dynamically count the repos we provided)
        # This tests that len() works properly on the filtered repository list
        expected_repos = [mock_repo1, mock_repo2]
        self.assertIn(f'Total public repositories: {len(expected_repos)}', result.output)

    @patch('github_cleaner.core.Github')
    def test_public_repos_active_filter(self, mock_github):
        # Set up mock repos
        mock_repo1 = MockRepository(
            name='active-repo',
            private=False,
            archived=False,
            description='Active public repo'
        )
        
        mock_repo2 = MockRepository(
            name='archived-repo',
            private=False,
            archived=True,
            description='Archived public repo'
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the command with active filter
        result = self.runner.invoke(cli, ['public', 'testuser', '--filter', 'active'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check if the output contains the expected title
        self.assertIn('Active Public Repositories for @testuser', result.output)
        
        # Check if only the active repository is in the output
        self.assertIn('active-repo', result.output)
        self.assertNotIn('archived-repo', result.output)
        
        # Check repository count (should only count active repos)
        # This tests filtering and len() functionality
        active_repos = [repo for repo in [mock_repo1, mock_repo2] if not repo.archived]
        self.assertIn(f'Total public repositories: {len(active_repos)}', result.output)

    @patch('github_cleaner.core.Github')
    def test_public_repos_archived_filter(self, mock_github):
        # Set up mock repos
        mock_repo1 = MockRepository(
            name='active-repo',
            private=False,
            archived=False,
            description='Active public repo'
        )
        
        mock_repo2 = MockRepository(
            name='archived-repo',
            private=False,
            archived=True,
            description='Archived public repo'
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the command with archived filter
        result = self.runner.invoke(cli, ['public', 'testuser', '--filter', 'archived'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check if the output contains the expected title
        self.assertIn('Archived Public Repositories for @testuser', result.output)
        
        # Check if only the archived repository is in the output
        self.assertIn('archived-repo', result.output)
        self.assertNotIn('active-repo', result.output)
        
        # Check repository count (should only count archived repos)
        # This tests filtering and len() functionality  
        archived_repos = [repo for repo in [mock_repo1, mock_repo2] if repo.archived]
        self.assertIn(f'Total public repositories: {len(archived_repos)}', result.output)

    @patch('github_cleaner.core.Github')
    def test_public_repos_user_not_found(self, mock_github):
        # Setup GitHub to raise a "Not Found" exception
        from github import GithubException
        mock_exception = GithubException(
            status=404,
            data={'message': 'Not Found'}
        )
        mock_github.return_value.get_user.side_effect = mock_exception
        
        # Run the command
        result = self.runner.invoke(cli, ['public', 'nonexistentuser'])
        
        # Check the command ran successfully (errors are handled within the command)
        self.assertEqual(result.exit_code, 0)
        
        # Verify specific user not found error was printed
        self.assertIn("User 'nonexistentuser' not found", result.output)

    @patch('github_cleaner.core.Github')
    def test_public_repos_github_exception(self, mock_github):
        # Setup GitHub to raise a general exception
        from github import GithubException
        mock_exception = GithubException(
            status=500,
            data={'message': 'Server Error'}
        )
        mock_github.return_value.get_user.side_effect = mock_exception
        
        # Run the command
        result = self.runner.invoke(cli, ['public', 'testuser'])
        
        # Check the command ran successfully (errors are handled within the command)
        self.assertEqual(result.exit_code, 0)
        
        # Verify GitHub error was printed
        self.assertIn('GitHub Error', result.output)

    @patch('github_cleaner.core.Github')
    def test_public_repos_no_repositories(self, mock_github):
        # Set up mock user with no repositories
        mock_user = MagicMock()
        mock_user.get_repos.return_value = []
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the command
        result = self.runner.invoke(cli, ['public', 'testuser'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check if the output shows zero repositories
        # This tests len() on an empty list
        empty_repos = []
        self.assertIn(f'Total public repositories: {len(empty_repos)}', result.output)
        
        # Check if the table title is still correct
        self.assertIn('All Public Repositories for @testuser', result.output)


if __name__ == '__main__':
    unittest.main()