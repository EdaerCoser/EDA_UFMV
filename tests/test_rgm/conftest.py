"""
Pytest configuration for RGM tests.

Disables pytest-qt plugin due to DLL loading issues on Windows.
"""

import sys

# Remove pytest-qt from loaded plugins
def pytest_configure(config):
    # Disable qt plugin
    if hasattr(config, 'pluginmanager'):
        config.pluginmanager.set_blocked('pytest-qt')
