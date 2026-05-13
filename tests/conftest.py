"""
Pytest configuration and shared fixtures for FastAPI app tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture that provides a TestClient instance for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture that resets activities to a clean state before each test."""
    from src.app import activities
    
    # Store original state
    original_activities = {
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
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays and learn theater skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and learn about scientific concepts",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": []
        }
    }
    
    # Clear and reset the activities dictionary
    activities.clear()
    activities.update({k: {**v, "participants": list(v["participants"])} for k, v in original_activities.items()})
    
    yield
    
    # Reset after test (in case test modifies it)
    activities.clear()
    activities.update({k: {**v, "participants": list(v["participants"])} for k, v in original_activities.items()})


@pytest.fixture
def sample_data():
    """Fixture providing sample data for tests."""
    return {
        "emails": {
            "new_student": "newstudent@mergington.edu",
            "another_student": "anotherstudent@mergington.edu",
            "existing_chess": "michael@mergington.edu",
            "existing_gym": "john@mergington.edu"
        },
        "activities": {
            "existing": "Chess Club",
            "empty": "Basketball Team",
            "nonexistent": "Nonexistent Club"
        }
    }
