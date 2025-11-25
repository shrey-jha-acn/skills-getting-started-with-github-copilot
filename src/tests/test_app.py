"""
Tests for the FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from app import app

# Create a test client
client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status code 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_duplicate_email_returns_400(self):
        """Test that signing up with duplicate email returns 400"""
        # First signup
        client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
        # Try duplicate signup
        response = client.post(
            "/activities/Chess Club/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        email = "unregister_test@mergington.edu"
        # First signup
        client.post(f"/activities/Tennis Club/signup?email={email}")
        # Then unregister
        response = client.post(f"/activities/Tennis Club/unregister?email={email}")
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_not_signed_up_returns_400(self):
        """Test that unregistering when not signed up returns 400"""
        response = client.post(
            "/activities/Drama Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregistering from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivityParticipantCount:
    """Tests for activity participant counts"""

    def test_participant_count_increases_after_signup(self):
        """Test that participant count increases after signup"""
        email = "participant_test@mergington.edu"
        # Get initial state
        response = client.get("/activities")
        initial_count = len(response.json()["Basketball Team"]["participants"])

        # Signup
        client.post(f"/activities/Basketball Team/signup?email={email}")

        # Get updated state
        response = client.get("/activities")
        updated_count = len(response.json()["Basketball Team"]["participants"])

        assert updated_count == initial_count + 1

    def test_participant_count_decreases_after_unregister(self):
        """Test that participant count decreases after unregister"""
        email = "unregister_count_test@mergington.edu"
        activity = "Art Studio"

        # Signup
        client.post(f"/activities/{activity}/signup?email={email}")

        # Get count after signup
        response = client.get("/activities")
        count_after_signup = len(response.json()[activity]["participants"])

        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")

        # Get count after unregister
        response = client.get("/activities")
        count_after_unregister = len(response.json()[activity]["participants"])

        assert count_after_unregister == count_after_signup - 1
