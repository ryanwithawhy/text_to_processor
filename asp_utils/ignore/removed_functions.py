# REMOVED FUNCTIONS - DO NOT IMPORT
# Functions removed due to confusion with stream processing workflows

def execute_mongodb_command(
    mongodb_url: str,
    database: str,
    command: str
) -> tuple[bool, str, str]:
    """
    Execute MongoDB shell commands against a regular MongoDB cluster.
    
    Args:
        mongodb_url: Full MongoDB connection string including credentials
                    (e.g., mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true)
        database: Database name to connect to
        command: JavaScript/MongoDB shell command to execute
        
    Returns:
        tuple: (success, stdout, stderr)
    """
    import subprocess
    from urllib.parse import urlparse
    
    # For mongodb+srv URLs, we connect to the URL directly and specify database in the command
    # For other URLs, we might need to append the database
    if mongodb_url.startswith('mongodb+srv://') or mongodb_url.startswith('mongodb://'):
        full_url = mongodb_url
    else:
        # Legacy handling - ensure URL ends with exactly one slash
        if not mongodb_url.endswith('/'):
            mongodb_url += '/'
        full_url = f"{mongodb_url}{database}"
    
    # Wrap command in an aborted transaction for safety (prevents any writes)
    # Connect directly to the database and execute command without "use" statement
    safe_command = f"""
    session = db.getMongo().startSession();
    session.startTransaction();
    try {{
        result = ({command});
        print(typeof result === 'object' ? JSON.stringify(result) : result);
    }} catch (e) {{
        print('Error:', e);
        throw e;
    }} finally {{
        session.abortTransaction();
        session.endSession();
    }}
    """
    
    # Build mongosh command - connect directly to database to avoid "switched to db" message
    # For mongodb+srv URLs, append the database name if not already present
    if mongodb_url.startswith('mongodb+srv://') or mongodb_url.startswith('mongodb://'):
        # Parse the URL to check if database is already specified
        parsed = urlparse(mongodb_url)
        
        # If no database in path or path is just '/', add the database
        if not parsed.path or parsed.path == '/':
            if parsed.query:
                database_url = f"{parsed.scheme}://{parsed.netloc}/{database}?{parsed.query}"
            else:
                database_url = f"{parsed.scheme}://{parsed.netloc}/{database}"
        else:
            # Database already specified in URL, use as-is but connect to specified database
            database_url = mongodb_url
    else:
        database_url = full_url
    
    mongosh_cmd = [
        'mongosh',
        database_url,
        '--eval', safe_command
    ]
    
    try:
        print(f"Executing MongoDB command on {database}: {command}")
        result = subprocess.run(mongosh_cmd, capture_output=True, text=True, timeout=60)
        
        return (result.returncode == 0, result.stdout, result.stderr)
        
    except subprocess.TimeoutExpired:
        error_msg = f"✗ Timeout executing MongoDB command"
        print(error_msg)
        return (False, "", error_msg)
    except Exception as e:
        error_msg = f"✗ Unexpected error executing MongoDB command: {e}"
        print(error_msg)
        return (False, "", error_msg)