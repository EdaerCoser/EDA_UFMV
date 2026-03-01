"""
Custom test runner to disable pytest-qt plugin
"""

import os
import sys
import pytest

# Disable pytest-qt plugin to avoid Windows DLL loading issues
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

if __name__ == '__main__':
    sys.exit(pytest.main([
        'tests/test_api/test_complex_stress.py::TestGradualStress::test_gradual_stress_from_small_to_large',
        '-v',
        '-s',
        '--include-slow'  # Include slow tests
    ]))
