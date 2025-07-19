#!/usr/bin/env python3
"""
Unit tests for MongoDB command execution functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess

# Add parent directory to path to import asp_utils
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from asp_utils import execute_mongodb_command


class TestExecuteMongoDBCommand(unittest.TestCase):
    """Test cases for execute_mongodb_command function."""
    
    @patch('subprocess.run')
    def test_execute_command_success(self, mock_run):
        """Test successful MongoDB command execution."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="{ count: 5 }",
            stderr=""
        )
        
        success, stdout, stderr = execute_mongodb_command(
            "mongodb://test-user:test-password@test-cluster.example.com",
            "test_db",
            "db.collection.countDocuments()"
        )
        
        self.assertTrue(success)
        self.assertEqual(stdout, "{ count: 5 }")
        self.assertEqual(stderr, "")
        mock_run.assert_called_once()
        
        # Verify the mongosh command structure
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], 'mongosh')
        self.assertEqual(args[1], 'mongodb://test-user:test-password@test-cluster.example.com/test_db')
        self.assertIn('--eval', args)
        
        # Check that the command is wrapped in transaction code
        eval_arg = args[args.index('--eval') + 1]
        self.assertIn('db.collection.countDocuments()', eval_arg)
        self.assertIn('session.startTransaction()', eval_arg)
        self.assertIn('session.abortTransaction()', eval_arg)
    
    @patch('subprocess.run')
    def test_execute_command_failure(self, mock_run):
        """Test MongoDB command execution failure."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Authentication failed"
        )
        
        success, stdout, stderr = execute_mongodb_command(
            "mongodb://wrong-user:wrong-password@test-cluster.example.com",
            "test_db",
            "db.stats()"
        )
        
        self.assertFalse(success)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Authentication failed")
    
    @patch('subprocess.run', side_effect=subprocess.TimeoutExpired(['mongosh'], 60))
    def test_execute_command_timeout(self, mock_run):
        """Test MongoDB command execution timeout."""
        success, stdout, stderr = execute_mongodb_command(
            "mongodb://test-user:test-password@slow-cluster.example.com",
            "test_db",
            "db.collection.find()"
        )
        
        self.assertFalse(success)
        self.assertEqual(stdout, "")
        self.assertIn("Timeout", stderr)
    
    @patch('subprocess.run', side_effect=Exception("Network error"))
    def test_execute_command_exception(self, mock_run):
        """Test MongoDB command execution with unexpected exception."""
        success, stdout, stderr = execute_mongodb_command(
            "mongodb://test-user:test-password@unreachable-cluster.example.com",
            "test_db",
            "db.stats()"
        )
        
        self.assertFalse(success)
        self.assertEqual(stdout, "")
        self.assertIn("Unexpected error", stderr)
        self.assertIn("Network error", stderr)
    
    @patch('subprocess.run')
    def test_url_formatting(self, mock_run):
        """Test that MongoDB URLs are formatted correctly."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Test mongodb+srv URL (standard Atlas format)
        execute_mongodb_command(
            "mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true",
            "mydb", 
            "db.stats()"
        )
        
        args = mock_run.call_args[0][0]
        self.assertEqual(args[1], 'mongodb+srv://user:pass@cluster.mongodb.net/mydb?retryWrites=true')
        
        # Test regular mongodb URL
        mock_run.reset_mock()
        execute_mongodb_command(
            "mongodb://user:pass@cluster.example.com",
            "mydb",
            "db.stats()"
        )
        
        args = mock_run.call_args[0][0]
        self.assertEqual(args[1], 'mongodb://user:pass@cluster.example.com/mydb')
    
    @patch('subprocess.run')
    def test_complex_commands(self, mock_run):
        """Test execution of complex MongoDB commands."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"_id": 1, "name": "test"}]',
            stderr=""
        )
        
        complex_command = 'db.orders.find({status: "pending"}).limit(5).toArray()'
        
        success, stdout, stderr = execute_mongodb_command(
            "mongodb://user:pass@cluster.example.com",
            "sales",
            complex_command
        )
        
        self.assertTrue(success)
        self.assertIn('"name": "test"', stdout)
        
        # Verify the command was passed correctly (wrapped in transaction code)
        args = mock_run.call_args[0][0]
        eval_arg = args[args.index('--eval') + 1]
        self.assertIn(complex_command, eval_arg)


if __name__ == '__main__':
    unittest.main()