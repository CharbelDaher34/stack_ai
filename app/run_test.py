def run_test_file(test_file: str):
    """Run a test file."""
    import pytest
    pytest.main([test_file])

if __name__ == "__main__":
    run_test_file("./tests/test_index.py")