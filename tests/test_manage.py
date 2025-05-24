import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import tempfile
from click.testing import CliRunner

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import cli, read_repository_list, perform_repository_operation

# Create a mock for GitHub Repository objects
class MockRepository:
    def __init__(self, name, full_name=None, archived=False):
        self.name = name
        self.full_name = full_name or f"testuser/{name}"
        self.archived = archived
    
    def edit(self, archived=None):
        if archived is not None:
            self.archived = archived
    
    def delete(self):
        pass  # Mock deletion


class TestManageCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
    
    def test_read_repository_list_success(self):
        """Test reading repository list from file."""
        # Create temporary file with repo names
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("user1/repo1\n")
            temp_file.write("user2/repo2\n")
            temp_file.write("\n")  # Empty line should be filtered
            temp_file.write("  user3/repo3  \n")  # Whitespace should be stripped
            temp_filename = temp_file.name
        
        try:
            repos = read_repository_list(temp_filename)
            self.assertEqual(repos, ["user1/repo1", "user2/repo2", "user3/repo3"])
        finally:
            os.unlink(temp_filename)
    
    def test_read_repository_list_file_not_found(self):
        """Test error handling when file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            read_repository_list("nonexistent-file.txt")
    
    def test_read_repository_list_empty_file(self):
        """Test handling of empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("\n\n   \n")  # Only whitespace/empty lines
            temp_filename = temp_file.name
        
        try:
            repos = read_repository_list(temp_filename)
            self.assertEqual(repos, [])
        finally:
            os.unlink(temp_filename)
    
    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    def test_perform_archive_operation_success(self, mock_get_token, mock_github):
        """Test successful archive operation."""
        # Set up mock repository
        mock_repo = MockRepository("test-repo", "testuser/test-repo", archived=False)
        mock_github.return_value.get_repo.return_value = mock_repo
        
        # Perform operation
        result = perform_repository_operation(mock_github.return_value, "testuser/test-repo", "archive")
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["operation"], "archive")
        self.assertIn("Successfully archived", result["details"])
        self.assertTrue(mock_repo.archived)
    
    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    def test_perform_archive_already_archived(self, mock_get_token, mock_github):
        """Test archive operation on already archived repository."""
        # Set up mock repository that's already archived
        mock_repo = MockRepository("test-repo", "testuser/test-repo", archived=True)
        mock_github.return_value.get_repo.return_value = mock_repo
        
        # Perform operation
        result = perform_repository_operation(mock_github.return_value, "testuser/test-repo", "archive")
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["operation"], "archive")
        self.assertIn("Already archived", result["details"])
    
    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    def test_perform_delete_operation_success(self, mock_get_token, mock_github):
        """Test successful delete operation."""
        # Set up mock repository
        mock_repo = MockRepository("test-repo", "testuser/test-repo")
        mock_github.return_value.get_repo.return_value = mock_repo
        
        # Perform operation
        result = perform_repository_operation(mock_github.return_value, "testuser/test-repo", "delete")
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["operation"], "delete")
        self.assertIn("Successfully deleted", result["details"])
    
    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    def test_perform_operation_repo_not_found(self, mock_get_token, mock_github):
        """Test operation on non-existent repository."""
        from github import GithubException
        
        # Set up mock to raise not found exception
        mock_exception = GithubException(404, {'message': 'Not Found'})
        mock_github.return_value.get_repo.side_effect = mock_exception
        
        # Perform operation
        result = perform_repository_operation(mock_github.return_value, "user/nonexistent", "archive")
        
        # Verify result
        self.assertFalse(result["success"])
        self.assertEqual(result["operation"], "archive")
        self.assertIn("Repository not found", result["details"])
    
    @patch('main.Github')
    @patch('main.get_github_token', return_value='fake-token')
    def test_perform_operation_permission_error(self, mock_get_token, mock_github):
        """Test operation with insufficient permissions."""
        from github import GithubException
        
        # Set up mock to raise permission exception
        mock_exception = GithubException(403, {'message': 'Must have admin permission'})
        mock_github.return_value.get_repo.side_effect = mock_exception
        
        # Perform operation
        result = perform_repository_operation(mock_github.return_value, "user/repo", "delete")
        
        # Verify result
        self.assertFalse(result["success"])
        self.assertEqual(result["operation"], "delete")
        self.assertIn("Insufficient permissions", result["details"])
    
    def test_manage_command_file_not_found(self):
        """Test manage command with non-existent file."""
        result = self.runner.invoke(cli, ['manage', 'nonexistent.txt', 'archive'])
        
        # Should exit with error code and show error message
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("does not exist", result.output.lower())
    
    def test_manage_command_invalid_operation(self):
        """Test manage command with invalid operation."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("user/repo\n")
            temp_filename = temp_file.name
        
        try:
            result = self.runner.invoke(cli, ['manage', temp_filename, 'invalid'])
            
            # Should show error for invalid choice
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid value", result.output)
        finally:
            os.unlink(temp_filename)
    
    @patch('main.confirm_operation', return_value=False)
    def test_manage_command_user_cancels(self, mock_confirm):
        """Test manage command when user cancels operation."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("user/repo\n")
            temp_filename = temp_file.name
        
        try:
            result = self.runner.invoke(cli, ['manage', temp_filename, 'archive'])
            
            # Should show cancellation message
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Operation cancelled", result.output)
            mock_confirm.assert_called_once_with("archive", 1)
        finally:
            os.unlink(temp_filename)
    
    @patch('main.perform_repository_operation')
    @patch('main.init_github_client')
    @patch('main.confirm_operation', return_value=True)
    def test_manage_command_successful_operations(self, mock_confirm, mock_github_client, mock_perform_op):
        """Test manage command with successful operations."""
        # Set up mocks
        mock_perform_op.side_effect = [
            {"repo_name": "user/repo1", "operation": "archive", "success": True, "details": "Successfully archived"},
            {"repo_name": "user/repo2", "operation": "archive", "success": True, "details": "Already archived"}
        ]
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("user/repo1\nuser/repo2\n")
            temp_filename = temp_file.name
        
        try:
            result = self.runner.invoke(cli, ['manage', temp_filename, 'archive'])
            
            # Should complete successfully
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Operation Summary", result.output)
            self.assertIn("2 successful, 0 failed", result.output)
            
            # Verify operations were called
            self.assertEqual(mock_perform_op.call_count, 2)
        finally:
            os.unlink(temp_filename)
    
    @patch('main.perform_repository_operation')
    @patch('main.init_github_client')
    @patch('main.confirm_operation', return_value=True)
    def test_manage_command_mixed_results(self, mock_confirm, mock_github_client, mock_perform_op):
        """Test manage command with mixed success/failure results."""
        # Set up mocks with mixed results
        mock_perform_op.side_effect = [
            {"repo_name": "user/repo1", "operation": "delete", "success": True, "details": "Successfully deleted"},
            {"repo_name": "user/repo2", "operation": "delete", "success": False, "details": "Repository not found"}
        ]
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("user/repo1\nuser/repo2\n")
            temp_filename = temp_file.name
        
        try:
            result = self.runner.invoke(cli, ['manage', temp_filename, 'delete'])
            
            # Should complete successfully but show failures
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Operation Summary", result.output)
            self.assertIn("1 successful, 1 failed", result.output)
            self.assertIn("Some operations failed", result.output)
        finally:
            os.unlink(temp_filename)
    
    def test_manage_command_empty_file(self):
        """Test manage command with empty repository file."""
        # Create empty file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("")
            temp_filename = temp_file.name
        
        try:
            result = self.runner.invoke(cli, ['manage', temp_filename, 'archive'])
            
            # Should show no repositories found error
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No repositories found", result.output)
        finally:
            os.unlink(temp_filename)


if __name__ == '__main__':
    unittest.main()