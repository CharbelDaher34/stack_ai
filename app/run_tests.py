#!/usr/bin/env python3
"""
Test runner script to ensure all tests are discovered and executed.
This script provides detailed information about test discovery and execution.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests_with_verbose_output():
    """Run tests with verbose output to see which tests are being called."""
    print("🚀 Starting comprehensive test run...")
    print("=" * 60)
    
    # Change to the app directory if we're not already there
    if not os.path.exists("tests"):
        os.chdir("app")
    
    # First, discover all tests
    print("🔍 Discovering all tests...")
    discovery_cmd = [
        sys.executable, "-m", "pytest", 
        "--collect-only", 
        "-q",
        "tests/"
    ]
    
    try:
        result = subprocess.run(discovery_cmd, capture_output=True, text=True)
        print("📋 Test Discovery Results:")
        print(result.stdout)
        if result.stderr:
            print("⚠️ Discovery Warnings/Errors:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error during test discovery: {e}")
    
    print("\n" + "=" * 60)
    
    # Run tests with maximum verbosity
    print("🧪 Running all tests with verbose output...")
    test_cmd = [
        sys.executable, "-m", "pytest",
        "-v",  # verbose
        "-s",  # don't capture output (show print statements)
        "--tb=short",  # shorter traceback format
        "--durations=10",  # show 10 slowest tests
        "tests/test_index.py"
    ]
    
    try:
        result = subprocess.run(test_cmd, text=True)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

def check_test_functions():
    """Check which test functions are defined in the test file."""
    print("\n🔍 Analyzing test file for test functions...")
    
    test_file = Path("tests/test_index.py")
    if not test_file.exists():
        test_file = Path("app/tests/test_index.py")
    
    if test_file.exists():
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Find all test functions
        import re
        test_functions = re.findall(r'def (test_\w+)', content)
        
        print(f"📝 Found {len(test_functions)} test functions:")
        for i, func in enumerate(test_functions, 1):
            print(f"  {i}. {func}")
        
        # Check for non-test functions that might be tests
        all_functions = re.findall(r'def (\w+)', content)
        potential_tests = [f for f in all_functions if not f.startswith('test_') and f not in ['db_session', 'index_builder']]
        
        if potential_tests:
            print(f"\n⚠️ Found {len(potential_tests)} functions that might be tests but don't start with 'test_':")
            for func in potential_tests:
                print(f"  - {func}")
            print("  💡 These won't be automatically discovered by pytest!")
    else:
        print("❌ Test file not found!")

def main():
    """Main function to run comprehensive test analysis."""
    print("🧪 Comprehensive Test Runner")
    print("=" * 60)
    
    # Check test functions first
    check_test_functions()
    
    print("\n" + "=" * 60)
    
    # Run the tests
    exit_code = run_tests_with_verbose_output()
    
    print("\n" + "=" * 60)
    print("📊 Test Run Summary:")
    if exit_code == 0:
        print("✅ All tests passed successfully!")
    else:
        print(f"❌ Tests failed with exit code: {exit_code}")
    
    print("\n💡 Tips for ensuring all tests run:")
    print("  1. All test functions must start with 'test_'")
    print("  2. Test files must start with 'test_' or end with '_test.py'")
    print("  3. Use 'pytest -v' to see which tests are running")
    print("  4. Use 'pytest --collect-only' to see test discovery")
    print("  5. Check for syntax errors that might prevent test discovery")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main()) 