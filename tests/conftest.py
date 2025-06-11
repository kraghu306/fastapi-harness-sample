
"""
Pytest configuration file.
"""
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Import common fixtures and utilities here
import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app) 
