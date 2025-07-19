#!/usr/bin/env python3
"""
Integration tests for MongoDB command execution functionality.

These tests require a real MongoDB connection and will be skipped if no config file is found.
To run these tests, create a mongodb_test_config.json file with your MongoDB credentials.
"""

import unittest
import json
import os
from pathlib import Path

# Add parent directory to path to import asp_utils
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from asp_utils import execute_mongodb_command


class TestMongoDBIntegration(unittest.TestCase):
    """Integration tests for MongoDB command execution."""
    
    @classmethod
    def setUpClass(cls):
        """Load MongoDB test configuration if available."""
        # Look for config file in the tests directory
        config_path = Path(__file__).parent / "mongodb_test_config.json"
        
        if not config_path.exists():
            cls.skip_tests = True
            cls.skip_reason = f"MongoDB test config not found at {config_path}"
            return
        
        try:
            with open(config_path, 'r') as f:
                cls.config = json.load(f)
            
            # Validate required fields
            required_fields = ["mongodb-url", "database", "collection"]
            missing_fields = [field for field in required_fields if field not in cls.config]
            
            if missing_fields:
                cls.skip_tests = True
                cls.skip_reason = f"Missing required config fields: {missing_fields}"
                return
                
            cls.skip_tests = False
            
        except Exception as e:
            cls.skip_tests = True
            cls.skip_reason = f"Error loading config: {e}"
    
    def setUp(self):
        """Skip tests if configuration is not available."""
        if self.skip_tests:
            self.skipTest(self.skip_reason)
    
    def test_connection_and_basic_query(self):
        """Test that we can connect and query the production collection."""
        success, stdout, stderr = execute_mongodb_command(
            self.config["mongodb-url"],
            self.config["database"],
            f"db.{self.config['collection']}.findOne()"
        )
        
        self.assertTrue(success, f"Failed to connect or query: {stderr}")
        # Should return either a document or null
        self.assertTrue("null" in stdout or "{" in stdout, 
                       f"Expected valid query result, got: {stdout}")
    
    def test_count_documents(self):
        """Test counting documents in the production collection."""
        success, stdout, stderr = execute_mongodb_command(
            self.config["mongodb-url"],
            self.config["database"],
            f"db.{self.config['collection']}.countDocuments({{}})"
        )
        
        self.assertTrue(success, f"Failed to count documents: {stderr}")
        # Should return a number
        self.assertTrue(any(char.isdigit() for char in stdout), 
                       f"Expected numeric count, got: {stdout}")
    
    def test_sample_documents(self):
        """Test sampling a few documents from the production collection."""
        success, stdout, stderr = execute_mongodb_command(
            self.config["mongodb-url"],
            self.config["database"],
            f"db.{self.config['collection']}.find().limit(3).toArray()"
        )
        
        self.assertTrue(success, f"Failed to sample documents: {stderr}")
        # Should return an array
        self.assertTrue(stdout.strip().startswith('['), 
                       f"Expected array result, got: {stdout}")


if __name__ == '__main__':
    unittest.main()