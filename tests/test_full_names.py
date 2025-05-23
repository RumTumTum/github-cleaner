import unittest
from unittest.mock import patch, MagicMock
import os
import sys
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


class TestFullNamesFlag(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
    
    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    def test_list_command_default_shows_repo_names(self, mock_get_token, mock_github):
        # Set up mock repos
        mock_repo = MockRepository(
            name='test-repo',
            full_name='testuser/test-repo'
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the list command without --full-names
        result = self.runner.invoke(cli, ['list'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify just repo name is shown, not full name
        self.assertIn('test-repo', result.output)
        self.assertNotIn('testuser/test-repo', result.output)

    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    def test_list_command_with_full_names_shows_full_names(self, mock_get_token, mock_github):
        # Set up mock repos
        mock_repo = MockRepository(
            name='test-repo',
            full_name='testuser/test-repo'
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the list command with --full-names
        result = self.runner.invoke(cli, ['list', '--full-names'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify full name is shown in table
        self.assertIn('testuser/test-repo', result.output)

    @patch('main.Github')
    def test_public_command_default_shows_repo_names(self, mock_github):
        # Set up mock repos
        mock_repo = MockRepository(
            name='public-repo',
            full_name='octocat/public-repo'
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the public command without --full-names
        result = self.runner.invoke(cli, ['public', 'octocat'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify just repo name is shown, not full name
        self.assertIn('public-repo', result.output)
        self.assertNotIn('octocat/public-repo', result.output)

    @patch('main.Github')
    def test_public_command_with_full_names_shows_full_names(self, mock_github):
        # Set up mock repos
        mock_repo = MockRepository(
            name='public-repo',
            full_name='octocat/public-repo'
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.return_value.get_user.return_value = mock_user
        
        # Run the public command with --full-names
        result = self.runner.invoke(cli, ['public', 'octocat', '--full-names'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify full name is shown in table
        self.assertIn('octocat/public-repo', result.output)

    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    def test_list_command_full_names_with_filter(self, mock_get_token, mock_github):
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
        
        # Run the list command with --full-names and filter
        result = self.runner.invoke(cli, ['list', '--filter', 'active', '--full-names'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify full name of active repo is shown
        self.assertIn('testuser/active-repo', result.output)
        # Verify archived repo is not shown
        self.assertNotIn('testuser/archived-repo', result.output)

    @patch('main.Github')
    def test_public_command_full_names_with_filter(self, mock_github):
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
        
        # Run the public command with --full-names and filter
        result = self.runner.invoke(cli, ['public', 'octocat', '--filter', 'archived', '--full-names'])
        
        # Check the command ran successfully
        self.assertEqual(result.exit_code, 0)
        
        # Verify full name of archived repo is shown
        self.assertIn('octocat/archived-repo', result.output)
        # Verify active repo is not shown
        self.assertNotIn('octocat/active-repo', result.output)

    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    def test_full_names_flag_doesnt_affect_export(self, mock_get_token, mock_github):
        # Set up mock repos
        mock_repo = MockRepository(
            name='test-repo',
            full_name='testuser/test-repo'
        )
        
        # Set up mock user and github
        mock_user = MagicMock()
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.return_value.get_user.return_value = mock_user
        
        from unittest.mock import mock_open
        with patch('builtins.open', mock_open()) as mock_file:
            # Run the list command with --full-names and --export
            result = self.runner.invoke(cli, ['list', '--full-names', '--export', 'test.txt'])
            
            # Check the command ran successfully
            self.assertEqual(result.exit_code, 0)
            
            # Verify export still uses full names (should not be affected by --full-names)
            mock_file().write.assert_called_once_with('testuser/test-repo\n')
            
            # Verify export message shown (no table display)
            self.assertIn('Exported 1 all repositories', result.output)
            self.assertNotIn('Total repositories:', result.output)

    def test_create_repository_table_function_directly(self):
        """Test the create_repository_table function directly with full_names parameter."""
        from main import create_repository_table
        from rich.console import Console
        import io
        
        # Create test repositories
        mock_repos = [
            MockRepository(name='repo1', full_name='user1/repo1'),
            MockRepository(name='repo2', full_name='user2/repo2'),
        ]
        
        # Test without full_names (default)
        table_normal = create_repository_table(mock_repos, "Test", full_names=False)
        
        # Capture table output
        console = Console(file=io.StringIO(), width=120)
        console.print(table_normal)
        table_normal_str = console.file.getvalue()
        
        # Should contain repo names only
        self.assertIn('repo1', table_normal_str)
        self.assertIn('repo2', table_normal_str)
        # Should not contain full names in the content
        self.assertNotIn('user1/repo1', table_normal_str)
        self.assertNotIn('user2/repo2', table_normal_str)
        
        # Test with full_names=True
        table_full = create_repository_table(mock_repos, "Test", full_names=True)
        
        # Capture table output
        console_full = Console(file=io.StringIO(), width=120)
        console_full.print(table_full)
        table_full_str = console_full.file.getvalue()
        
        # Should contain full names
        self.assertIn('user1/repo1', table_full_str)
        self.assertIn('user2/repo2', table_full_str)


if __name__ == '__main__':
    unittest.main()