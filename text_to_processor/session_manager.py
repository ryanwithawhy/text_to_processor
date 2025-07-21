#!/usr/bin/env python3
"""
Session Manager for Text to Processor

Manages session folders and audit trails for CLI wrapper usage.
Each conversation gets its own timestamped session folder.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class SessionManager:
    """Manages session folders and audit trail for CLI wrapper usage."""
    
    def __init__(self, base_dir: str = "temp"):
        self.base_dir = Path(base_dir)
        self.sessions_dir = self.base_dir / "sessions"
        self.current_session_file = self.base_dir / "current_session.txt"
        self.config_counter = 1
        
        # Ensure directories exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def get_current_session(self) -> str:
        """
        Get the current session folder name.
        Creates a new session if none exists or current is invalid.
        
        Returns:
            str: Session folder name (e.g., "2025-01-20_14-30-15")
        """
        # Check if current session file exists and is valid
        if self.current_session_file.exists():
            try:
                with open(self.current_session_file, 'r') as f:
                    session_name = f.read().strip()
                
                # Verify session folder exists
                session_path = self.sessions_dir / session_name
                if session_path.exists():
                    return session_name
            except Exception:
                pass
        
        # Create new session
        return self._create_new_session()
    
    def _create_new_session(self) -> str:
        """Create a new session folder with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_name = timestamp
        session_path = self.sessions_dir / session_name
        
        # Create session folder
        session_path.mkdir(exist_ok=True)
        
        # Create session metadata
        metadata = {
            "session_id": session_name,
            "created_at": datetime.now().isoformat(),
            "config_count": 0,
            "description": "Atlas Stream Processing session"
        }
        
        metadata_file = session_path / "session_info.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update current session file
        with open(self.current_session_file, 'w') as f:
            f.write(session_name)
        
        print(f"📁 Created new session: {session_name}")
        return session_name
    
    def create_new_session(self) -> str:
        """Force creation of a new session, regardless of existing sessions."""
        return self._create_new_session()
    
    def get_session_path(self) -> Path:
        """Get the full path to the current session folder."""
        session_name = self.get_current_session()
        return self.sessions_dir / session_name
    
    def get_next_config_filename(self, prefix: str = "config") -> str:
        """
        Get the next config filename with auto-incrementing number.
        
        Args:
            prefix: Prefix for the config file (default: "config")
            
        Returns:
            str: Filename like "001_config.json", "002_examine_data.json", etc.
        """
        session_path = self.get_session_path()
        
        # Find existing config files to determine next number
        existing_configs = list(session_path.glob("*.json"))
        
        # Filter out session_info.json
        config_files = [f for f in existing_configs if f.name != "session_info.json"]
        
        # Get next number
        next_num = len(config_files) + 1
        
        # Generate filename
        filename = f"{next_num:03d}_{prefix}.json"
        return filename
    
    def create_config_file(self, config_data: Dict[str, Any], prefix: str = "config") -> Path:
        """
        Create a new config file in the current session with auto-incrementing name.
        
        Args:
            config_data: Dictionary containing configuration data
            prefix: Prefix for the config file name
            
        Returns:
            Path: Full path to the created config file
        """
        session_path = self.get_session_path()
        filename = self.get_next_config_filename(prefix)
        config_path = session_path / filename
        
        # Add metadata to config
        config_with_metadata = {
            "created_at": datetime.now().isoformat(),
            "session_id": session_path.name,
            "config_type": prefix,
            **config_data
        }
        
        # Write config file
        with open(config_path, 'w') as f:
            json.dump(config_with_metadata, f, indent=2)
        
        # Update session metadata
        self._update_session_metadata()
        
        print(f"📝 Created config: {filename}")
        return config_path
    
    def _update_session_metadata(self):
        """Update session metadata with current config count."""
        session_path = self.get_session_path()
        metadata_file = session_path / "session_info.json"
        
        # Count config files (excluding session_info.json)
        config_files = [f for f in session_path.glob("*.json") if f.name != "session_info.json"]
        config_count = len(config_files)
        
        # Update metadata
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        metadata.update({
            "config_count": config_count,
            "updated_at": datetime.now().isoformat()
        })
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def list_sessions(self) -> list:
        """List all available sessions."""
        if not self.sessions_dir.exists():
            return []
        
        sessions = []
        for session_dir in self.sessions_dir.iterdir():
            if session_dir.is_dir():
                metadata_file = session_dir / "session_info.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    sessions.append(metadata)
                else:
                    # Session without metadata
                    sessions.append({
                        "session_id": session_dir.name,
                        "created_at": "unknown",
                        "config_count": len(list(session_dir.glob("*.json")))
                    })
        
        return sorted(sessions, key=lambda x: x.get("created_at", ""), reverse=True)


def get_session_manager() -> SessionManager:
    """Get a SessionManager instance for the current working directory."""
    return SessionManager()


if __name__ == "__main__":
    # Demo usage
    sm = SessionManager()
    
    print("Current session:", sm.get_current_session())
    print("Session path:", sm.get_session_path())
    
    # Create sample config
    sample_config = {
        "connection_user": "test_user",
        "connection_password": "test_pass",
        "operation": "test"
    }
    
    config_path = sm.create_config_file(sample_config, "test_config")
    print(f"Created config at: {config_path}")
    
    # List sessions
    print("\nAvailable sessions:")
    for session in sm.list_sessions():
        print(f"  {session['session_id']}: {session.get('config_count', 0)} configs")