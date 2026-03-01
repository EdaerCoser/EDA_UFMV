#!/usr/bin/env python
"""
RGM Test Runner

Runs RGM tests with proper environment configuration.
Disables pytest-qt plugin to avoid Windows DLL loading issues.
"""

import os
import sys
import subprocess

def main():
    # Disable pytest-qt plugin and other plugins that may cause issues
    os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

    # Run RGM tests
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/test_rgm/', '-v', '--tb=short'] + sys.argv[1:],
        env=os.environ,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

    return result.returncode

if __name__ == '__main__':
    sys.exit(main())
