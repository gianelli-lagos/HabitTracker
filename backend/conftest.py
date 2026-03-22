"""
Root conftest for pytest
Prevents pytest from collecting Lambda handler files as tests
"""
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def pytest_collection_modifyitems(session, config, items):
    """
    Remove any items collected from lambdas directory
    This prevents lambda_handler functions from being treated as tests
    """
    # Filter out anything from lambdas/
    items[:] = [
        item for item in items 
        if 'lambdas' not in str(item.fspath)
    ]

# Ignore lambdas directory during collection
collect_ignore_glob = ['lambdas/**']