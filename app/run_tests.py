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
    for test_file in Path("tests").glob("test_*.py"):
        print(f"🔍 Analyzing {test_file}...")
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

def run_single_test_file(test_file):
    """Run a single test file with verbose output."""
    print(f"\n🧪 Running tests in {test_file}...")
    print("=" * 60)
    
    test_cmd = [
        sys.executable, "-m", "pytest",
        "-v",  # verbose
        "-s",  # don't capture output
        "--tb=short",  # shorter traceback format
        "--durations=10",  # show 10 slowest tests
        str(test_file)
    ]
    
    try:
        result = subprocess.run(test_cmd, text=True)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running tests in {test_file}: {e}")
        return 1

def run_all_test_files_individually():
    """Run each test file separately and report results."""
    print("\n🧪 Running all test files individually...")
    print("=" * 60)
    
    test_files = list(Path("tests").glob("test_*.py"))
    if not test_files:
        print("❌ No test files found!")
        return 1
    
    results = {}
    for test_file in test_files:
        exit_code = run_single_test_file(test_file)
        results[test_file] = exit_code
        print(f"\n📊 Result for {test_file}: {'✅ Passed' if exit_code == 0 else '❌ Failed'}")
    
    print("\n" + "=" * 60)
    print("📊 Individual Test Files Summary:")
    all_passed = True
    for test_file, exit_code in results.items():
        status = "✅ Passed" if exit_code == 0 else "❌ Failed"
        print(f"{status}: {test_file}")
        if exit_code != 0:
            all_passed = False
    
    return 0 if all_passed else 1

def main():
    """Main function to run comprehensive test analysis."""
    print("🧪 Comprehensive Test Runner")
    print("=" * 60)
    
    # Check test functions first
    check_test_functions()
    
    print("\n" + "=" * 60)
    
    # Run each test file individually
    exit_code = run_all_test_files_individually()
    
    print("\n" + "=" * 60)
    print("📊 Test Run Summary:")
    if exit_code == 0:
        print("✅ All test files passed successfully!")
    else:
        print(f"❌ Some test files failed with exit code: {exit_code}")
    
    print("\n💡 Tips for ensuring all tests run:")
    print("  1. All test functions must start with 'test_'")
    print("  2. Test files must start with 'test_' or end with '_test.py'")
    print("  3. Use 'pytest -v' to see which tests are running")
    print("  4. Use 'pytest --collect-only' to see test discovery")
    print("  5. Check for syntax errors that might prevent test discovery")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main()) 