import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import tempfile
from click.testing import CliRunner

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from github_cleaner.cli import cli

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


class TestExportFlag(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
    
    @patch('github_cleaner.core.Github')
    @patch('github_cleaner.core.get_github_token', return_value='fake-token')
    @patch('builtins.open', new_callable=mock_open)
    def test_list_command_with_export_flag(self, mock_file, mock_get_token, mock_github):
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
        
        # Run the list command with export
        result = self.runner.invoke(cli, ['list', '--export', 'test-repos.txt'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify GitHub was called with token
        mock_github.assert_called_once_with('fake-token')
        
        # Verify file was opened
        mock_file.assert_called_once_with('test-repos.txt', 'w')
        
        # Verify full repository names were written
        mock_file().write.assert_any_call('testuser/repo1\n')
        mock_file().write.assert_any_call('testuser/repo2\n')
        
        # Verify success message (no table display)
        self.assertIn('Exported 2 all repositories to test-repos.txt', result.output)
        self.assertNotIn('Total repositories:', result.output)  # Table not shown

    @patch('github_cleaner.core.Github')
    @patch('github_cleaner.core.get_github_token', return_value='fake-token')
    @patch('builtins.open', new_callable=mock_open)
    def test_list_command_with_export_and_filter(self, mock_file, mock_get_token, mock_github):
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
        
        # Run the list command with active filter and export
        result = self.runner.invoke(cli, ['list', '--filter', 'active', '--export', 'active-repos.txt'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify file was opened with correct name
        mock_file.assert_called_once_with('active-repos.txt', 'w')
        
        # Verify only active repo was written
        mock_file().write.assert_called_once_with('testuser/active-repo\n')
        
        # Verify success message shows filtered count
        self.assertIn('Exported 1 active repositories to active-repos.txt', result.output)

    @patch('github_cleaner.core.Github')
    def test_public_command_with_export_flag(self, mock_github):
        # Set up mock repos
        mock_repo1 = MockRepository(
            name='public-repo1',
            full_name='octocat/public-repo1',
            archived=False
        )
        
        mock_repo2 = MockRepository(
            name='public-repo2',
            full_name='octocat/public-repo2',
            archived=True
        )
        
        # Set up mock user and github (no authentication)
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Use temporary file for real file writing test
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Run the public command with export
            result = self.runner.invoke(cli, ['public', 'octocat', '--export', temp_filename])
            
            # Check the command ran successfully
            self.assertEqual(result.exit_code, 0)
            
            # Verify GitHub was called without authentication
            mock_github.assert_called_once_with()
            
            # Verify get_user was called with username
            mock_github.return_value.get_user.assert_called_once_with('octocat')
            
            # Verify get_repos was called with type='public'
            mock_user.get_repos.assert_called_once_with(type='public')
            
            # Read the actual file and verify content
            with open(temp_filename, 'r') as f:
                content = f.read()
            
            self.assertIn('octocat/public-repo1\n', content)
            self.assertIn('octocat/public-repo2\n', content)
            
            # Verify success message includes username
            self.assertIn('Exported 2 all public repositories for @octocat', result.output)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_filename)

    @patch('github_cleaner.core.Github')
    def test_public_command_with_export_and_filter(self, mock_github):
        # Set up mock repos
        mock_repo1 = MockRepository(
            name='active-repo',
            full_name='octocat/active-repo',
            archived=False
        )
        
        mock_repo2 = MockRepository(
            name='archived-repo',
            full_name='octocat/archived-repo',
            archived=True
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Use temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Run the public command with archived filter and export
            result = self.runner.invoke(cli, ['public', 'octocat', '--filter', 'archived', '--export', temp_filename])
            
            # Check the command ran successfully
            self.assertEqual(result.exit_code, 0)
            
            # Read the file and verify only archived repo is there
            with open(temp_filename, 'r') as f:
                content = f.read()
            
            self.assertIn('octocat/archived-repo\n', content)
            self.assertNotIn('octocat/active-repo\n', content)
            
            # Verify success message
            self.assertIn('Exported 1 archived public repositories for @octocat', result.output)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_filename)

    @patch('github_cleaner.core.Github')
    @patch('github_cleaner.core.get_github_token', return_value='fake-token')
    def test_list_command_without_export_shows_table(self, mock_get_token, mock_github):
        # Set up mock repos
        mock_repo = MockRepository(name='test-repo', full_name='testuser/test-repo')
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the list command without export
        result = self.runner.invoke(cli, ['list'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify table is displayed (not export)
        self.assertIn('All GitHub Repositories', result.output)
        self.assertIn('Total repositories: 1', result.output)
        self.assertNotIn('Exported', result.output)

    @patch('github_cleaner.core.Github')
    def test_public_command_without_export_shows_table(self, mock_github):
        # Set up mock repos
        mock_repo = MockRepository(name='test-repo', full_name='octocat/test-repo')
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the public command without export
        result = self.runner.invoke(cli, ['public', 'octocat'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify table is displayed (not export)
        self.assertIn('All Public Repositories for @octocat', result.output)
        self.assertIn('Total public repositories: 1', result.output)
        self.assertNotIn('Exported', result.output)

    @patch('github_cleaner.core.Github')
    @patch('github_cleaner.core.get_github_token', return_value='fake-token')
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_export_file_permission_error(self, mock_file, mock_get_token, mock_github):
        # Set up mock repos
        mock_repo = MockRepository(name='test-repo', full_name='testuser/test-repo')
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the list command with export
        result = self.runner.invoke(cli, ['list', '--export', '/invalid/path/file.txt'])
        
        # Check the command ran successfully (errors are handled)
        self.assertEqual(result.exit_code, 0)
        
        # Verify error was printed
        self.assertIn('Error', result.output)
        self.assertIn('Permission denied', result.output)

    def test_export_validates_full_name_format(self):
        """Test that export uses full_name (owner/repo) format, not just repo name."""
        # Test the export_repositories function directly
        from github_cleaner.core import export_repositories
        
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