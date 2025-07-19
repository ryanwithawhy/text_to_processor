#!/usr/bin/env python3
"""
Configuration utilities for Atlas Stream Processing

Functions for loading, validating, and handling configuration files.
"""

import json
from typing import Dict, Any, Optional


def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error: Failed to read {file_path}: {e}")
        return None


def validate_main_config(config: Dict[str, Any]) -> bool:
    """Validate the main configuration file."""
    required_fields = [
        "confluent-cluster-id", 
        "confluent-rest-endpoint",
        "mongodb-stream-processor-instance-url",
        "stream-processor-prefix",
        "kafka-connection-name",
        "mongodb-connection-name",
        "mongodb-cluster-name",
        "mongodb-group-id",
        "mongodb-tenant-name"
    ]
    
    for field in required_fields:
        if field not in config:
            print(f"Error: Missing required field '{field}' in main config")
            return False
    
    return True