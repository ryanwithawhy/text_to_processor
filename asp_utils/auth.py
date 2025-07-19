#!/usr/bin/env python3
"""
Authentication utilities for MongoDB Atlas

Functions for handling MongoDB Atlas CLI authentication.
"""

import subprocess


def check_atlas_auth_with_login() -> bool:
    """
    Check if authenticated with Atlas CLI and prompt for login if not authenticated.
    Returns True if authenticated (or becomes authenticated), False if user declines login.
    """
    try:
        # Check current authentication status
        auth_check = subprocess.run(['atlas', 'auth', 'whoami'], capture_output=True, text=True, timeout=10)
        if auth_check.returncode == 0:
            print("✓ Already authenticated with Atlas CLI")
            return True
    except Exception as e:
        print(f"✗ Error checking Atlas CLI authentication: {e}")
        return False
    
    # Not authenticated - prompt user for login
    print("✗ Not authenticated with Atlas CLI")
    
    try:
        # Prompt user with default yes
        response = input("Would you like to login now? [Y/n]: ").strip().lower()
        
        # Default to 'yes' if empty response
        if response == '' or response == 'y' or response == 'yes':
            print("Running: atlas auth login")
            try:
                # Run atlas auth login interactively
                login_result = subprocess.run(['atlas', 'auth', 'login'], timeout=120)
                
                if login_result.returncode == 0:
                    print("✓ Successfully authenticated with Atlas CLI")
                    return True
                else:
                    print("✗ Failed to authenticate with Atlas CLI")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("✗ Login process timed out")
                return False
            except Exception as e:
                print(f"✗ Error during login: {e}")
                return False
        else:
            print("✗ Cannot proceed without Atlas CLI authentication")
            print("  Please run 'atlas auth login' manually and try again")
            return False
            
    except KeyboardInterrupt:
        print("\n✗ Login cancelled by user")
        return False
    except Exception as e:
        print(f"✗ Error during login prompt: {e}")
        return False