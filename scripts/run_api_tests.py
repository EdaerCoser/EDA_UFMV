#!/usr/bin/env python
"""Run API tests without pytest-qt plugin"""
import sys
import os

# Disable pytest plugins
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

# Run pytest programmatically
import pytest
sys.exit(pytest.main([
    'tests/test_api/',
    '-v',
    '--tb=short',
    '-p', 'no:qt'
]))
