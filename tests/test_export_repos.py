import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import tempfile
from click.testing import CliRunner

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import cli

# Create a mock for GitHub Repository objects
class MockRepository:
    def __init__(self, name, full_name=None, private=False, archived=False, description=""):
        self.name = name
        self.full_name = full_name or f"testuser/{name}"
        self.private = private
        self.archived = archived
        self.description = description
    
    def __str__(self):
        return self.name


class TestExportRepositories(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
    
    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_all_repos_default_filename(self, mock_file, mock_get_token, mock_github):
        # Set up mock repos
        mock_repo1 = MockRepository(
            name='repo1',
            full_name='testuser/repo1',
            archived=False
        )
        
        mock_repo2 = MockRepository(
            name='repo2', 
            full_name='testuser/repo2',
            archived=True
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the export command
        result = self.runner.invoke(cli, ['export'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify GitHub was called with token
        mock_github.assert_called_once_with('fake-token')
        
        # Verify file was opened with default name
        mock_file.assert_called_once_with('repositories.txt', 'w')
        
        # Verify full repository names were written (not just names)
        mock_file().write.assert_any_call('testuser/repo1\n')
        mock_file().write.assert_any_call('testuser/repo2\n')
        
        # Verify success message
        self.assertIn('Exported 2 all repositories to repositories.txt', result.output)

    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_active_repos_custom_filename(self, mock_file, mock_get_token, mock_github):
        # Set up mock repos
        mock_repo1 = MockRepository(
            name='active-repo',
            full_name='testuser/active-repo',
            archived=False
        )
        
        mock_repo2 = MockRepository(
            name='archived-repo',
            full_name='testuser/archived-repo', 
            archived=True
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the export command with active filter and custom filename
        result = self.runner.invoke(cli, ['export', '--filter', 'active', '--output', 'active-repos.txt'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify file was opened with custom name
        mock_file.assert_called_once_with('active-repos.txt', 'w')
        
        # Verify only active repo was written
        mock_file().write.assert_called_once_with('testuser/active-repo\n')
        
        # Verify success message shows filtered count
        self.assertIn('Exported 1 active repositories to active-repos.txt', result.output)

    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_archived_repos(self, mock_file, mock_get_token, mock_github):
        # Set up mock repos
        mock_repo1 = MockRepository(
            name='active-repo',
            full_name='testuser/active-repo',
            archived=False
        )
        
        mock_repo2 = MockRepository(
            name='archived-repo',
            full_name='testuser/archived-repo',
            archived=True
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the export command with archived filter
        result = self.runner.invoke(cli, ['export', '--filter', 'archived'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify only archived repo was written
        mock_file().write.assert_called_once_with('testuser/archived-repo\n')
        
        # Verify success message
        self.assertIn('Exported 1 archived repositories', result.output)

    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_no_repositories(self, mock_file, mock_get_token, mock_github):
        # Set up mock user with no repositories
        mock_user = MagicMock()
        mock_user.get_repos.return_value = []
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the export command
        result = self.runner.invoke(cli, ['export'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify file was opened
        mock_file.assert_called_once_with('repositories.txt', 'w')
        
        # Verify no writes occurred (empty repo list)
        mock_file().write.assert_not_called()
        
        # Verify success message shows zero count
        self.assertIn('Exported 0 all repositories', result.output)

    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    def test_export_github_exception(self, mock_get_token, mock_github):
        # Setup GitHub to raise an exception
        from github import GithubException
        mock_exception = GithubException(
            status=500,
            data={'message': 'Server Error'}
        )
        mock_github.return_value.get_user.side_effect = mock_exception
        
        # Run the export command
        result = self.runner.invoke(cli, ['export'])
        
        # Check the command ran successfully (errors are handled)
        self.assertEqual(result.exit_code, 0)
        
        # Verify GitHub error was printed
        self.assertIn('GitHub Error', result.output)

    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_export_file_permission_error(self, mock_file, mock_get_token, mock_github):
        # Set up mock repos
        mock_repo = MockRepository(name='test-repo', full_name='testuser/test-repo')
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the export command
        result = self.runner.invoke(cli, ['export'])
        
        # Check the command ran successfully (errors are handled)
        self.assertEqual(result.exit_code, 0)
        
        # Verify error was printed
        self.assertIn('Error', result.output)
        self.assertIn('Permission denied', result.output)

    def test_export_validates_full_name_format(self):
        """Test that export uses full_name (owner/repo) format, not just repo name."""
        # Test the export_repositories function directly
        from main import export_repositories
        
        # Create mock repositories with different owners
        mock_repos = [
            MockRepository(name='repo1', full_name='user1/repo1'),
            MockRepository(name='repo2', full_name='user2/repo2'),
            MockRepository(name='same-name', full_name='user1/same-name'),
            MockRepository(name='same-name', full_name='user2/same-name'),
        ]
        
        # Use temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Export repositories
            export_repositories(mock_repos, temp_filename)
            
            # Read the file and verify content
            with open(temp_filename, 'r') as f:
                content = f.read()
            
            # Verify full names are used, not just repo names
            self.assertIn('user1/repo1\n', content)
            self.assertIn('user2/repo2\n', content)
            self.assertIn('user1/same-name\n', content)
            self.assertIn('user2/same-name\n', content)
            
            # Verify the content contains slashes (indicating full names)
            lines = content.strip().split('\n')
            for line in lines:
                self.assertIn('/', line, f"Line '{line}' should contain '/' for full name format")
            
            # Verify we have exactly 4 lines
            self.assertEqual(len(lines), 4)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_filename)


if __name__ == '__main__':
    unittest.main()