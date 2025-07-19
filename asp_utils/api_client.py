#!/usr/bin/env python3
"""
MongoDB Atlas Stream Processing API Client

Functions for creating and managing MongoDB Atlas Stream Processing resources
including connections, stream processors, and Kafka topics.
"""

import json
import subprocess
import requests
from typing import Dict, Any, Optional, Union, List


def create_mongodb_connection(
    group_id: str,
    tenant_name: str,
    cluster_name: str,
    connection_name: str,
    role_name: str = "readAnyDatabase",
    role_type: str = "BUILT_IN"
) -> tuple[bool, bool]:
    """Create a MongoDB Atlas Stream Processing connection using Atlas CLI."""
    
    # Create connection configuration
    connection_config = {
        "type": "Cluster",
        "clusterName": cluster_name,
        "dbRoleToExecute": {
            "role": role_name,
            "type": role_type
        }
    }
    
    # Write temporary config file
    temp_config_file = "temporary-connection-file.json"
    try:
        with open(temp_config_file, 'w') as f:
            json.dump(connection_config, f, indent=2)
        
        # Create MongoDB connection using Atlas CLI
        cmd = [
            'atlas', 'streams', 'connections', 'create',
            connection_name,
            '--projectId', group_id,
            '--instance', tenant_name,
            '--file', temp_config_file,
            '--output', 'json'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✓ Successfully created MongoDB connection: {connection_name}")
            return True, True  # success, was_created
        else:
            # Check if connection already exists
            if "already exists" in result.stderr.lower() or "duplicate" in result.stderr.lower():
                print(f"⚠ MongoDB connection already exists, reusing: {connection_name}")
                return True, False  # success, was_created
            else:
                print(f"✗ Failed to create MongoDB connection {connection_name}")
                print(f"  Error: {result.stderr}")
                return False, False  # success, was_created
                
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout creating MongoDB connection {connection_name}")
        return False, False
    except Exception as e:
        print(f"✗ Unexpected error creating MongoDB connection {connection_name}: {e}")
        return False, False
    finally:
        # Clean up temporary file
        import os
        if os.path.exists(temp_config_file):
            os.remove(temp_config_file)


def create_kafka_connection(
    group_id: str,
    tenant_name: str,
    connection_name: str,
    confluent_rest_endpoint: str,
    kafka_api_key: str,
    kafka_api_secret: str
) -> tuple[bool, bool]:
    """Create a MongoDB Atlas Stream Processing Kafka connection using Atlas CLI."""
    
    # Convert bootstrap servers from REST endpoint
    bootstrap_servers = confluent_rest_endpoint.replace('https://', '').replace(':443', ':9092')
    
    # Create connection configuration
    connection_config = {
        "name": connection_name,
        "type": "Kafka",
        "authentication": {
            "mechanism": "PLAIN",
            "username": kafka_api_key,
            "password": kafka_api_secret
        },
        "bootstrapServers": bootstrap_servers,
        "config": {
            "auto.offset.reset": "earliest",
            "group.id": f"{connection_name}-consumer-group"
        },
        "security": {
            "protocol": "SASL_SSL"
        }
    }
    
    # Write temporary config file
    temp_config_file = f"/tmp/{connection_name}_config.json"
    try:
        with open(temp_config_file, 'w') as f:
            json.dump(connection_config, f, indent=2)
        
        # Create Kafka connection using Atlas CLI
        cmd = [
            'atlas', 'streams', 'connection', 'create',
            connection_name,
            '--projectId', group_id,
            '--instance', tenant_name,
            '--file', temp_config_file,
            '--output', 'json'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✓ Successfully created Kafka connection: {connection_name}")
            return True, True  # success, was_created
        else:
            # Check if connection already exists
            if "already exists" in result.stderr.lower() or "duplicate" in result.stderr.lower():
                print(f"⚠ Kafka connection already exists, reusing: {connection_name}")
                return True, False  # success, was_created
            else:
                print(f"✗ Failed to create Kafka connection {connection_name}")
                print(f"  Error: {result.stderr}")
                return False, False  # success, was_created
                
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout creating Kafka connection {connection_name}")
        return False, False
    except Exception as e:
        print(f"✗ Unexpected error creating Kafka connection {connection_name}: {e}")
        return False, False
    finally:
        # Clean up temporary file
        import os
        if os.path.exists(temp_config_file):
            os.remove(temp_config_file)


def execute_stream_processing_javascript(
    connection_user: str,
    connection_password: str,
    stream_processor_url: str,
    javascript_shell_code: str
) -> tuple[bool, str, str]:
    """
    Execute MongoDB Shell JavaScript against the stream processing instance.
    
    Args:
        connection_user: MongoDB user for authentication
        connection_password: MongoDB password for authentication  
        stream_processor_url: MongoDB stream processor instance URL
        javascript_shell_code: JavaScript code to execute in MongoDB Shell
        
    Returns:
        tuple: (success, stdout, stderr)
    """
    
    # Ensure URL ends with exactly one slash
    if not stream_processor_url.endswith('/'):
        stream_processor_url += '/'
    
    # Build mongosh command
    mongosh_cmd = [
        'mongosh',
        stream_processor_url,
        '--tls',
        '--authenticationDatabase', 'admin',
        '--username', connection_user,
        '--password', connection_password,
        '--eval', javascript_shell_code
    ]
    
    try:
        print(f"Executing JavaScript: {javascript_shell_code}")
        result = subprocess.run(mongosh_cmd, capture_output=True, text=True, timeout=60)
        
        return (result.returncode == 0, result.stdout, result.stderr)
        
    except subprocess.TimeoutExpired:
        error_msg = f"✗ Timeout executing JavaScript code"
        print(error_msg)
        return (False, "", error_msg)
    except Exception as e:
        error_msg = f"✗ Unexpected error executing JavaScript code: {e}"
        print(error_msg)
        return (False, "", error_msg)


def create_stream_processor(
    connection_user: str,
    connection_password: str,
    stream_processor_url: str,
    stream_processor_name: str,
    pipeline: List[Dict[str, Any]]
) -> bool:
    """
    Create a stream processor with a custom pipeline using mongosh and sp.createStreamProcessor.
    
    Args:
        connection_user: MongoDB user for authentication
        connection_password: MongoDB password for authentication  
        stream_processor_url: MongoDB stream processor instance URL
        stream_processor_name: Name of the stream processor
        pipeline: List of pipeline stages for the stream processor
        
    Returns:
        bool: True if stream processor was created successfully, False otherwise
    """
    
    # Create JavaScript command for mongosh
    pipeline_json = json.dumps(pipeline)
    js_command = f'sp.createStreamProcessor("{stream_processor_name}", {pipeline_json})'
    
    # Execute the JavaScript code
    success, stdout, stderr = execute_stream_processing_javascript(
        connection_user,
        connection_password,
        stream_processor_url,
        js_command
    )
    
    if success:
        # Check if creation was successful or if it already exists
        if "already exists" in stderr.lower() or "duplicate" in stderr.lower():
            print(f"⚠ Stream processor already exists: {stream_processor_name}")
            return True
        else:
            print(f"✓ Successfully created stream processor: {stream_processor_name}")
            return True
    else:
        # Check for already exists error in stderr
        if "already exists" in stderr.lower() or "duplicate" in stderr.lower():
            print(f"⚠ Stream processor already exists: {stream_processor_name}")
            return True
        else:
            print(f"✗ Failed to create stream processor {stream_processor_name}")
            print(f"  Error: {stderr}")
            return False


def process_temporary_pipeline(
    connection_user: str,
    connection_password: str,
    stream_processor_url: str,
    pipeline: List[Dict[str, Any]],
    dlq: Optional[str] = None,
    dry_run: bool = False
) -> tuple[bool, str, str]:
    """
    Execute a temporary pipeline using sp.process().
    
    Args:
        connection_user: MongoDB user for authentication
        connection_password: MongoDB password for authentication  
        stream_processor_url: MongoDB stream processor instance URL
        pipeline: List of pipeline stages to execute
        dlq: Dead letter queue name (optional)
        dry_run: Whether to run in dry-run mode (default: False)
        
    Returns:
        tuple: (success, stdout, stderr)
    """
    
    # Create JavaScript command for sp.process()
    pipeline_json = json.dumps(pipeline)
    
    # Build options object
    options = {}
    if dlq is not None:
        options["dlq"] = dlq
    if dry_run:
        options["dryRun"] = True
    
    # Create the JavaScript command
    if options:
        options_json = json.dumps(options)
        js_command = f'sp.process({pipeline_json}, {options_json})'
    else:
        js_command = f'sp.process({pipeline_json})'
    
    # Execute the JavaScript code
    return execute_stream_processing_javascript(
        connection_user,
        connection_password,
        stream_processor_url,
        js_command
    )


def create_simple_mongodb_to_kafka_topic_pipeline(
    mongodb_connection_name: str,
    database: str,
    collection: str,
    kafka_connection_name: str,
    topic: str
) -> List[Dict[str, Any]]:
    """
    Create a simple MongoDB -> Kafka pipeline.
    
    Args:
        mongodb_connection_name: Name of the MongoDB connection
        database: Database name
        collection: Collection name
        kafka_connection_name: Name of the Kafka connection
        topic: Kafka topic name
        
    Returns:
        List of pipeline stages
    """
    return [
        {
            "$source": {
                "connectionName": mongodb_connection_name,
                "db": database,
                "coll": collection
            }
        },
        {
            "$emit": {
                "connectionName": kafka_connection_name,
                "topic": topic
            }
        }
    ]


def create_simple_kafka_topic_to_mongodb_pipeline(
    kafka_connection_name: str,
    topics: Union[str, List[str]],
    mongodb_connection_name: str,
    database: str,
    collection: str,
    auto_offset_reset: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Create a simple Kafka -> MongoDB pipeline.
    
    Args:
        kafka_connection_name: Name of the Kafka connection
        topics: Kafka topic(s) to consume from
        mongodb_connection_name: Name of the MongoDB connection
        database: Database name
        collection: Collection name
        auto_offset_reset: Auto offset reset strategy
        
    Returns:
        List of pipeline stages
    """
    # Create the $source stage for Kafka input
    source_stage = {
        "connectionName": kafka_connection_name,
        "topic": topics
    }
    
    # Add config with auto_offset_reset if provided
    if auto_offset_reset:
        source_stage["config"] = {
            "auto_offset_reset": auto_offset_reset
        }
    
    return [
        {
            "$source": source_stage
        },
        {
            "$merge": {
                "into": {
                    "connectionName": mongodb_connection_name,
                    "db": database,
                    "coll": collection
                }
            }
        }
    ]


def create_topic(
    rest_endpoint: str,
    cluster_id: str,
    api_key: str,
    api_secret: str,
    topic_name: str
) -> bool:
    """Create a Kafka topic using the Confluent REST API."""
    
    url = f"{rest_endpoint}/kafka/v3/clusters/{cluster_id}/topics"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "topic_name": topic_name,
        "partitions_count": 3,
        "configs": [
            {"name": "cleanup.policy", "value": "delete"}
        ]
    }
    
    try:
        response = requests.post(
            url,
            auth=(api_key, api_secret),
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 201:
            print(f"✓ Successfully created topic: {topic_name}")
            return True
        elif response.status_code == 409:
            print(f"⚠ Topic already exists: {topic_name}")
            return True
        else:
            # Check if the error is specifically error code 40002
            try:
                response_json = response.json()
                error_code = response_json.get('error_code')
                if error_code == 40002:
                    print(f"ℹ Topic {topic_name} is already created")
                    return True
            except (json.JSONDecodeError, KeyError):
                pass
            
            print(f"✗ Failed to create topic {topic_name}: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error creating topic {topic_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error creating topic {topic_name}: {e}")
        return False