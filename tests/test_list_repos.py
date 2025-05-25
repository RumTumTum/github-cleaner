import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from io import StringIO
from click.testing import CliRunner

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from github_cleaner.cli import cli

# Create a better mock for GitHub Repository objects
class MockRepository:
    def __init__(self, name, private=False, archived=False, description=""):
        self.name = name
        self.private = private
        self.archived = archived
        self.description = description
    
    def __str__(self):
        return self.name


class TestListRepositories(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
    
    @patch('github_cleaner.core.Github')
    @patch('github_cleaner.core.get_github_token', return_value='fake-token')
    def test_list_all_repos(self, mock_get_token, mock_github):
        # Set up mock repos using our custom MockRepository class
        mock_repo1 = MockRepository(
            name='repo1',
            private=False,
            archived=False,
            description='Test repo 1'
        )
        
        mock_repo2 = MockRepository(
            name='repo2',
            private=True,
            archived=True,
            description='Test repo 2'
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        # Configure get_repos to return a list directly so we can iterate over it multiple times
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the command
        result = self.runner.invoke(cli, ['list'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify GitHub token was used
        mock_github.assert_called_once_with('fake-token')
        
        # Verify repositories were requested
        mock_user.get_repos.assert_called()
        
        # Check if the output contains the expected title
        self.assertIn('All GitHub Repositories', result.output)
        
        # Check if both repository names are in the output
        self.assertIn('repo1', result.output)
        self.assertIn('repo2', result.output)

    @patch('github_cleaner.core.Github')
    @patch('github_cleaner.core.get_github_token', return_value='fake-token')
    def test_list_active_repos(self, mock_get_token, mock_github):
        # Set up mock repos using our custom MockRepository class
        mock_repo1 = MockRepository(
            name='repo1',
            private=False,
            archived=False,
            description='Active repo'
        )
        
        mock_repo2 = MockRepository(
            name='repo2',
            private=True,
            archived=True,
            description='Archived repo'
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the command
        result = self.runner.invoke(cli, ['list', '--filter', 'active'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check if the output contains the expected title
        self.assertIn('Active GitHub Repositories', result.output)
        
        # Check if only the active repository is in the output
        self.assertIn('repo1', result.output)

    @patch('github_cleaner.core.Github')
    @patch('github_cleaner.core.get_github_token', return_value='fake-token')
    def test_list_archived_repos(self, mock_get_token, mock_github):
        # Set up mock repos using our custom MockRepository class
        mock_repo1 = MockRepository(
            name='repo1',
            private=False,
            archived=False,
            description='Active repo'
        )
        
        mock_repo2 = MockRepository(
            name='repo2',
            private=True,
            archived=True,
            description='Archived repo'
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the command
        result = self.runner.invoke(cli, ['list', '--filter', 'archived'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Check if the output contains the expected title
        self.assertIn('Archived GitHub Repositories', result.output)
        
        # Check if only the archived repository is in the output
        self.assertIn('repo2', result.output)

    @patch('github_cleaner.core.Github')
    @patch('github_cleaner.core.get_github_token', return_value='fake-token')
    def test_handle_github_exception(self, mock_get_token, mock_github):
        # Setup GitHub to raise an exception
        from github import GithubException
        # Mock the exception with the right status code and data format
        mock_exception = GithubException(
            status=404,
            data={'message': 'Not Found'}
        )
        mock_github.return_value.get_user.side_effect = mock_exception
        
        # Run the command
        result = self.runner.invoke(cli, ['list'])
        
        # Check the command ran successfully (errors are handled within the command)
        self.assertEqual(result.exit_code, 0)
        
        # Verify error was printed
        self.assertIn('GitHub Error', result.output)


if __name__ == '__main__':
    unittest.main()
