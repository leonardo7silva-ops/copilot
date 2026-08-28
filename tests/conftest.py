"""
Pytest configuration and shared fixtures for FastAPI tests.

Provides:
- test_client: FastAPI TestClient instance for making HTTP requests
- fresh_activities: Fixture that resets the activities data for each test
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def test_client():
    """
    Fixture that provides a TestClient for the FastAPI app.
    
    Allows tests to make HTTP requests to the app without running a server.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities(monkeypatch):
    """
    Fixture that resets the activities data to a known state before each test.
    
    This ensures test isolation - each test starts with the default activities
    and doesn't affect other tests.
    
    Args:
        monkeypatch: pytest's monkeypatch fixture for mocking
    
    Returns:
        dict: A fresh copy of the activities dictionary
    """
    # Define fresh activities state
    fresh_data = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Practice soccer skills and compete in team matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 24,
            "participants": []
        },
        "Basketball Club": {
            "description": "Develop basketball skills and play competitive games",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore drawing, painting, and other visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Build acting skills and perform in school productions",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop public speaking, research, and argumentation skills",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Explore scientific concepts through experiments and projects",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": []
        }
    }
    
    # Clear existing activities and replace with fresh data
    activities.clear()
    activities.update(fresh_data)
    
    yield fresh_data
    
    # Cleanup: restore fresh state after test
    activities.clear()
    activities.update(fresh_data)
