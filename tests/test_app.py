"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the /activities endpoint"""
    
    def test_get_activities_returns_200(self):
        """Test that GET /activities returns 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self):
        """Test that the activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
    
    def test_participants_is_list(self):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Test the /activities/{activity_name}/signup endpoint"""
    
    def test_signup_returns_200_for_valid_input(self):
        """Test that signup returns 200 for valid inputs"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_signup_adds_participant(self):
        """Test that signup adds the participant to the activity"""
        email = "newemail123@mergington.edu"
        
        # Get initial participants
        response = client.get("/activities")
        initial_participants = response.json()["Chess Club"]["participants"].copy()
        
        # Sign up
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        new_participants = response.json()["Chess Club"]["participants"]
        
        assert email in new_participants
        assert len(new_participants) == len(initial_participants) + 1
    
    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "teststudent@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
    
    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_email_returns_400(self):
        """Test that signing up with duplicate email returns 400"""
        # michael@mergington.edu is already signed up for Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Test the /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_returns_200_for_valid_input(self):
        """Test that unregister returns 200 for valid inputs"""
        # First sign up a student
        email = "unregistertest@mergington.edu"
        client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": email}
        )
        
        # Then unregister them
        response = client.delete(
            "/activities/Tennis%20Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
    
    def test_unregister_removes_participant(self):
        """Test that unregister removes the participant from the activity"""
        email = "removetest@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        assert email in response.json()["Basketball Team"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Basketball%20Team/unregister",
            params={"email": email}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        assert email not in response.json()["Basketball Team"]["participants"]
    
    def test_unregister_returns_success_message(self):
        """Test that unregister returns a success message"""
        email = "removemsg@mergington.edu"
        
        # Sign up first
        client.post(
            "/activities/Debate%20Club/signup",
            params={"email": email}
        )
        
        # Unregister
        response = client.delete(
            "/activities/Debate%20Club/unregister",
            params={"email": email}
        )
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
    
    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregister for non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_signed_up_returns_400(self):
        """Test that unregistering a student not signed up returns 400"""
        response = client.delete(
            "/activities/Art%20Studio/unregister",
            params={"email": "notsignup@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
