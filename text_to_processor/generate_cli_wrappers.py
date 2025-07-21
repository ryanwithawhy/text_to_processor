#!/usr/bin/env python3
"""
CLI Wrapper Generator for ASP Utils

This script automatically generates CLI wrapper scripts for all functions
exported from the asp_utils package. Each wrapper reads a JSON config file
and calls the corresponding asp_utils function.

Usage:
    python generate_cli_wrappers.py

This will:
1. Delete all existing files in temp/ directory
2. Generate fresh CLI wrapper scripts for each asp_utils function
3. Place them in temp/ directory (untracked by git)
"""

import os
import sys
import shutil
import inspect
import json
from pathlib import Path

# Add parent directory to path to import asp_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asp_utils


def clean_temp_directory():
    """Remove and recreate the temp directory structure."""
    temp_dir = Path("temp")
    cli_wrappers_dir = temp_dir / "cli_wrappers"
    sessions_dir = temp_dir / "sessions"
    
    # Remove existing cli_wrappers directory (always regenerated)
    if cli_wrappers_dir.exists():
        print(f"🗑️  Removing existing CLI wrappers directory...")
        shutil.rmtree(cli_wrappers_dir)
    
    # Create temp directory structure
    print(f"📁 Creating temp directory structure...")
    temp_dir.mkdir(exist_ok=True)
    cli_wrappers_dir.mkdir(exist_ok=True)
    sessions_dir.mkdir(exist_ok=True)
    
    return cli_wrappers_dir


def get_asp_utils_functions():
    """Get all functions exported from asp_utils package."""
    functions = {}
    
    # Get all attributes from asp_utils
    for name in dir(asp_utils):
        if not name.startswith('_'):  # Skip private attributes
            attr = getattr(asp_utils, name)
            if callable(attr) and hasattr(attr, '__module__'):
                # Only include functions from asp_utils modules
                if attr.__module__.startswith('asp_utils'):
                    functions[name] = attr
    
    return functions


def generate_cli_wrapper(func_name, func, temp_dir):
    """Generate a CLI wrapper script for a single function."""
    
    # Get function signature
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    
    # Create the CLI script content
    script_content = f'''#!/usr/bin/env python3
"""
Auto-generated CLI wrapper for asp_utils.{func_name}

This script reads a JSON config file and calls asp_utils.{func_name}
with the parameters specified in the config.

Usage:
    python cli_{func_name}.py <config_file.json>

Config file format:
{{
{_generate_config_example(sig)}
}}
"""

import json
import sys
import os

# Add parent directory to path to import asp_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from asp_utils import {func_name}


def main():
    if len(sys.argv) != 2:
        print("Usage: python cli_{func_name}.py <config_file.json>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {{config_file}}")
        sys.exit(1)
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {{e}}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not read config file: {{e}}")
        sys.exit(1)
    
    try:
        # Extract parameters from config
{_generate_param_extraction(sig)}
        
        # Call the function
        print(f"Calling {func_name} with provided parameters...")
        result = {func_name}({', '.join(params)})
        
        # Output result
        if result is not None:
            if isinstance(result, (dict, list)):
                print("Result:")
                print(json.dumps(result, indent=2))
            elif isinstance(result, tuple):
                print("Result (tuple):")
                for i, item in enumerate(result):
                    print(f"  [{{i}}]: {{item}}")
            else:
                print(f"Result: {{result}}")
        else:
            print("Function completed successfully (no return value)")
            
    except KeyError as e:
        print(f"Error: Missing required parameter in config: {{e}}")
        sys.exit(1)
    except Exception as e:
        print(f"Error calling {func_name}: {{e}}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
    
    # Write the CLI script
    script_path = temp_dir / f"cli_{func_name}.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    
    return script_path


def _generate_config_example(sig):
    """Generate example config JSON for function signature."""
    lines = []
    for param_name, param in sig.parameters.items():
        if param.annotation != inspect.Parameter.empty:
            annotation = str(param.annotation).replace('typing.', '').replace('<class \'', '').replace('\'>', '')
        else:
            annotation = "value"
        
        if param.default != inspect.Parameter.empty:
            if isinstance(param.default, str):
                default_example = f'"{param.default}"'
            elif param.default is None:
                default_example = 'null'
            else:
                default_example = str(param.default)
            lines.append(f'    "{param_name}": {default_example}  // Optional, default: {param.default}')
        else:
            if 'str' in annotation.lower():
                example = '"your_value_here"'
            elif 'int' in annotation.lower():
                example = '123'
            elif 'bool' in annotation.lower():
                example = 'true'
            elif 'list' in annotation.lower() or 'List' in annotation:
                example = '["item1", "item2"]'
            elif 'dict' in annotation.lower() or 'Dict' in annotation:
                example = '{"key": "value"}'
            else:
                example = '"your_value_here"'
            lines.append(f'    "{param_name}": {example}')
    
    return ',\n'.join(lines)


def _generate_param_extraction(sig):
    """Generate parameter extraction code for function signature."""
    lines = []
    for param_name, param in sig.parameters.items():
        if param.default != inspect.Parameter.empty:
            # Optional parameter with default
            lines.append(f'        {param_name} = config.get("{param_name}", {repr(param.default)})')
        else:
            # Required parameter
            lines.append(f'        {param_name} = config["{param_name}"]')
    
    return '\n'.join(lines)


def main():
    """Main function to generate all CLI wrappers."""
    print("=" * 60)
    print("ASP Utils CLI Wrapper Generator")
    print("=" * 60)
    
    # Clean temp directory and get cli_wrappers dir
    cli_wrappers_dir = clean_temp_directory()
    
    # Create new session for this conversation
    print("🆕 Creating new session...")
    from session_manager import SessionManager
    session_manager = SessionManager()
    session_name = session_manager.create_new_session()
    print(f"📁 Created new session: {session_name}")
    
    # Get all asp_utils functions
    print("🔍 Discovering asp_utils functions...")
    functions = get_asp_utils_functions()
    
    if not functions:
        print("❌ No functions found in asp_utils!")
        return
    
    print(f"📋 Found {len(functions)} functions to wrap:")
    for func_name in sorted(functions.keys()):
        print(f"   • {func_name}")
    
    print()
    
    # Generate CLI wrappers
    print("🔧 Generating CLI wrappers...")
    generated_scripts = []
    
    for func_name, func in functions.items():
        try:
            script_path = generate_cli_wrapper(func_name, func, cli_wrappers_dir)
            generated_scripts.append(script_path)
            print(f"   ✅ {script_path.name}")
        except Exception as e:
            print(f"   ❌ Failed to generate wrapper for {func_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"✅ Successfully generated {len(generated_scripts)} CLI wrapper scripts")
    print(f"📁 Location: {cli_wrappers_dir}/")
    print()
    print("Usage examples:")
    for script in sorted(generated_scripts)[:3]:  # Show first 3 as examples
        print(f"   python {cli_wrappers_dir}/{script.name} temp/sessions/SESSION_FOLDER/config.json")
    if len(generated_scripts) > 3:
        print(f"   ... and {len(generated_scripts) - 3} more")
    print()
    print("🎉 Ready to use asp_utils functions via CLI!")


if __name__ == "__main__":
    main()