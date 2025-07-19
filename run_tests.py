#!/usr/bin/env python3
"""
Top-level test runner for all ASP Tools projects.

This script orchestrates testing across all subprojects in the asp_tools repository.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_asp_utils_tests():
    """Run tests for asp_utils shared utilities."""
    print("🧪 Running ASP Utils Tests")
    print("=" * 50)
    
    # Discover and run asp_utils tests
    test_dir = Path(__file__).parent / "asp_utils" / "tests"
    
    if not test_dir.exists():
        print("No asp_utils tests found")
        return True, 0, 0
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'unittest', 'discover',
            '-s', str(test_dir),
            '-p', 'test_*.py',
            '-v'
        ], capture_output=True, text=True, timeout=120)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Count tests from output - look for the final summary line
        lines = result.stdout.split('\n')
        test_count = 0
        
        # Look for "Ran X tests in Y.Ys" pattern
        for line in lines:
            line = line.strip()
            if line.startswith('Ran ') and ' tests in ' in line:
                try:
                    # Extract number between "Ran " and " tests"
                    # Example: "Ran 22 tests in 0.010s"
                    parts = line.split(' ')
                    if len(parts) >= 3 and parts[0] == 'Ran' and parts[2] == 'tests':
                        test_count = int(parts[1])
                        break
                except (IndexError, ValueError):
                    pass
        
        # If that fails, count individual test method lines as backup
        if test_count == 0:
            test_count = sum(1 for line in lines if line.strip().startswith('test_') and '...' in line)
        
        success = result.returncode == 0
        print(f"ASP Utils Tests: {'✅ PASSED' if success else '❌ FAILED'}")
        print("-" * 50)
        
        return success, test_count, 0 if success else 1
        
    except subprocess.TimeoutExpired:
        print("❌ ASP Utils tests timed out")
        return False, 0, 1
    except Exception as e:
        print(f"❌ Error running ASP Utils tests: {e}")
        return False, 0, 1


def run_confluent_config_to_asp_tests():
    """Run tests for confluent_config_to_asp project."""
    print("🧪 Running Confluent Config to ASP Tests")
    print("=" * 50)
    
    project_dir = Path(__file__).parent / "confluent_config_to_asp"
    run_tests_script = project_dir / "run_tests.py"
    
    if not run_tests_script.exists():
        print("No confluent_config_to_asp run_tests.py found")
        return True, 0, 0
    
    try:
        result = subprocess.run([
            sys.executable, str(run_tests_script)
        ], cwd=str(project_dir), capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        success = result.returncode == 0
        
        # Parse test counts from output
        lines = result.stdout.split('\n')
        unit_tests = 0
        integration_tests = 0
        failed_tests = 0
        
        for line in lines:
            # Look for "Tests run: X" in summaries
            if "Tests run:" in line and "unit" in line.lower():
                try:
                    unit_tests = int(line.split("Tests run:")[1].split(',')[0].strip())
                except:
                    pass
            elif "Tests run:" in line and "integration" in line.lower():
                try:
                    integration_tests = int(line.split("Tests run:")[1].split(',')[0].strip())
                except:
                    pass
            # Also look for "Ran X tests in Y.Ys" pattern for unittest output
            elif line.strip().startswith('Ran ') and ' tests in ' in line:
                try:
                    parts = line.strip().split(' ')
                    if len(parts) >= 3 and parts[0] == 'Ran' and parts[2] == 'tests':
                        test_count = int(parts[1])
                        # If we haven't found specific counts, use this as total
                        if unit_tests == 0 and integration_tests == 0:
                            integration_tests = test_count  # Assume integration for now
                except:
                    pass
            elif "Failures:" in line or "Errors:" in line:
                if not success:
                    failed_tests = max(failed_tests, 1)
        
        total_tests = unit_tests + integration_tests
        print(f"Confluent Config to ASP Tests: {'✅ PASSED' if success else '❌ FAILED'}")
        print("-" * 50)
        
        return success, total_tests, failed_tests
        
    except subprocess.TimeoutExpired:
        print("❌ Confluent Config to ASP tests timed out")
        return False, 0, 1
    except Exception as e:
        print(f"❌ Error running Confluent Config to ASP tests: {e}")
        return False, 0, 1


def run_text_to_processor_tests():
    """Run tests for text_to_processor project (when they exist)."""
    print("🧪 Running Text to Processor Tests")
    print("=" * 50)
    
    project_dir = Path(__file__).parent / "text_to_processor"
    run_tests_script = project_dir / "run_tests.py"
    
    if not run_tests_script.exists():
        print("No text_to_processor tests found - skipping")
        print("-" * 50)
        return True, 0, 0
    
    # TODO: Implement when text_to_processor has tests
    print("Text to Processor tests not yet implemented - skipping")
    print("-" * 50)
    return True, 0, 0


def main():
    """Run all tests across all projects."""
    print("🚀 ASP Tools - Running All Tests")
    print("=" * 60)
    
    total_tests = 0
    total_failures = 0
    all_passed = True
    
    # Run asp_utils tests
    asp_utils_passed, asp_utils_count, asp_utils_failures = run_asp_utils_tests()
    total_tests += asp_utils_count
    total_failures += asp_utils_failures
    all_passed = all_passed and asp_utils_passed
    
    # Run confluent_config_to_asp tests
    confluent_passed, confluent_count, confluent_failures = run_confluent_config_to_asp_tests()
    total_tests += confluent_count
    total_failures += confluent_failures
    all_passed = all_passed and confluent_passed
    
    # Run text_to_processor tests
    text_passed, text_count, text_failures = run_text_to_processor_tests()
    total_tests += text_count
    total_failures += text_failures
    all_passed = all_passed and text_passed
    
    # Print overall summary
    print("=" * 60)
    print("🎯 OVERALL TEST SUMMARY")
    print("=" * 60)
    print(f"  Overall result: {'🎉 ALL TESTS PASSED!' if all_passed else '💥 SOME TESTS FAILED'}")
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()