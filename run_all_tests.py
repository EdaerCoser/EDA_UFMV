#!/usr/bin/env python
"""
Comprehensive Test Runner for EDA_UFMV

Runs all tests with proper environment configuration.
Disables pytest-qt plugin to avoid Windows DLL loading issues.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, env=os.environ)
    success = result.returncode == 0
    status = "✓ PASSED" if success else "✗ FAILED"
    print(f"{description}: {status}\n")
    return success

def main():
    # Disable pytest-qt plugin to avoid Windows DLL loading issues
    os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

    project_dir = Path(__file__).parent.absolute()
    os.chdir(project_dir)

    print(f"EDA_UFMV Test Suite")
    print(f"Working directory: {project_dir}")
    print(f"Python version: {sys.version}")

    results = {}

    # 1. Coverage System Tests
    results['coverage'] = run_command(
        f'"{sys.executable}" run_coverage_tests.py',
        "Coverage System Tests (141 tests)"
    )

    # 2. RGM Tests
    results['rgm'] = run_command(
        f'"{sys.executable}" -m pytest tests/test_rgm/ -v --tb=short',
        "RGM System Tests (186+ tests)"
    )

    # 3. Legacy Randomization Tests
    results['legacy'] = run_command(
        f'"{sys.executable}" -m pytest tests/legacy/ -v --tb=short',
        "Legacy Randomization Tests (36 tests)"
    )

    # 4. Integration Tests
    results['integration'] = run_command(
        f'"{sys.executable}" -m pytest tests/integration/ -v --tb=short',
        "Integration Tests"
    )

    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for name, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {name}: {status}")

    print(f"\nTotal: {passed}/{total} test suites passed")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test suite(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
