"""
Atlas Stream Processing Utilities

Shared utilities for MongoDB Atlas Stream Processing operations,
including API clients, configuration handling, and authentication.
"""

from .api_client import (
    create_mongodb_connection,
    create_kafka_connection,
    create_stream_processor,
    create_topic
)

from .auth import check_atlas_auth_with_login

from .config_utils import (
    load_json_file,
    validate_main_config
)

__all__ = [
    'create_mongodb_connection',
    'create_kafka_connection', 
    'create_stream_processor',
    'create_topic',
    'check_atlas_auth_with_login',
    'load_json_file',
    'validate_main_config'
]