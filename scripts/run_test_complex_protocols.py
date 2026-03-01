"""
Test runner for test_complex_protocols.py that disables pytest-qt plugin
"""
import sys
import pytest

# Disable pytest-qt plugin
sys.argv.insert(1, '-p')
sys.argv.insert(2, 'no:qt')

# Add the test file
sys.argv.append('tests/test_api/test_complex_protocols.py')
sys.argv.append('-v')

# Run pytest
exit_code = pytest.main()
sys.exit(exit_code)
