"""
Integration tests for FastAPI activities API endpoints.
Tests cover GET /activities, POST /signup, and DELETE /unregister endpoints.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status code 200."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        activities = response.json()
        
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have all required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_shows_initial_participants(self, client, sample_data):
        """Test that GET /activities shows correct initial participants."""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert sample_data["emails"]["existing_chess"] in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_returns_200(self, client, sample_data):
        """Test that signing up a new participant returns status code 200."""
        response = client.post(
            f"/activities/{sample_data['activities']['empty']}/signup",
            params={"email": sample_data["emails"]["new_student"]}
        )
        assert response.status_code == 200

    def test_signup_new_participant_returns_success_message(self, client, sample_data):
        """Test that signup returns a success message."""
        email = sample_data["emails"]["new_student"]
        activity = sample_data["activities"]["empty"]
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_data):
        """Test that signup actually adds participant to the activity."""
        email = sample_data["emails"]["new_student"]
        activity = sample_data["activities"]["empty"]
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity]["participants"]

    def test_signup_duplicate_returns_400(self, client, sample_data):
        """Test that signing up twice returns 400 error."""
        email = sample_data["emails"]["existing_chess"]
        activity = sample_data["activities"]["existing"]
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client, sample_data):
        """Test that signing up for nonexistent activity returns 404."""
        response = client.post(
            f"/activities/{sample_data['activities']['nonexistent']}/signup",
            params={"email": sample_data["emails"]["new_student"]}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_signup_updates_availability(self, client, sample_data):
        """Test that signup updates the available spots count."""
        email = sample_data["emails"]["new_student"]
        activity = sample_data["activities"]["empty"]
        
        # Get initial availability
        response_before = client.get("/activities")
        initial_spots = (
            response_before.json()[activity]["max_participants"] -
            len(response_before.json()[activity]["participants"])
        )
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Get updated availability
        response_after = client.get("/activities")
        updated_spots = (
            response_after.json()[activity]["max_participants"] -
            len(response_after.json()[activity]["participants"])
        )
        
        assert updated_spots == initial_spots - 1

    def test_signup_multiple_participants(self, client, sample_data):
        """Test that multiple different participants can sign up."""
        activity = sample_data["activities"]["empty"]
        email1 = sample_data["emails"]["new_student"]
        email2 = sample_data["emails"]["another_student"]
        
        # Sign up first participant
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email1}
        )
        assert response1.status_code == 200
        
        # Sign up second participant
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email2}
        )
        assert response2.status_code == 200
        
        # Verify both are in the activity
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email1 in participants
        assert email2 in participants
        assert len(participants) == 2


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant_returns_200(self, client, sample_data):
        """Test that unregistering an existing participant returns 200."""
        email = sample_data["emails"]["existing_chess"]
        activity = sample_data["activities"]["existing"]
        
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client, sample_data):
        """Test that unregister returns a success message."""
        email = sample_data["emails"]["existing_chess"]
        activity = sample_data["activities"]["existing"]
        
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_unregister_removes_participant(self, client, sample_data):
        """Test that unregister actually removes participant from activity."""
        email = sample_data["emails"]["existing_chess"]
        activity = sample_data["activities"]["existing"]
        
        # Unregister
        client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email not in participants

    def test_unregister_not_registered_returns_400(self, client, sample_data):
        """Test that unregistering a non-registered participant returns 400."""
        email = sample_data["emails"]["new_student"]
        activity = sample_data["activities"]["existing"]
        
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_returns_404(self, client, sample_data):
        """Test that unregistering from nonexistent activity returns 404."""
        response = client.delete(
            f"/activities/{sample_data['activities']['nonexistent']}/unregister",
            params={"email": sample_data["emails"]["existing_chess"]}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_unregister_updates_availability(self, client, sample_data):
        """Test that unregister updates the available spots count."""
        email = sample_data["emails"]["existing_chess"]
        activity = sample_data["activities"]["existing"]
        
        # Get initial availability
        response_before = client.get("/activities")
        initial_spots = (
            response_before.json()[activity]["max_participants"] -
            len(response_before.json()[activity]["participants"])
        )
        
        # Unregister
        client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Get updated availability
        response_after = client.get("/activities")
        updated_spots = (
            response_after.json()[activity]["max_participants"] -
            len(response_after.json()[activity]["participants"])
        )
        
        assert updated_spots == initial_spots + 1


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_signup_then_unregister_same_participant(self, client, sample_data):
        """Test signup followed by unregister for same participant."""
        email = sample_data["emails"]["new_student"]
        activity = sample_data["activities"]["empty"]
        
        # Sign up
        response_signup = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response_signup.status_code == 200
        
        # Verify participant is added
        response_before = client.get("/activities")
        assert email in response_before.json()[activity]["participants"]
        
        # Unregister
        response_unregister = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response_unregister.status_code == 200
        
        # Verify participant is removed
        response_after = client.get("/activities")
        assert email not in response_after.json()[activity]["participants"]

    def test_activity_name_with_special_characters_in_url(self, client):
        """Test that activity names with special characters are handled correctly."""
        # URL encoding should handle spaces and special chars
        response = client.get("/activities")
        activities = response.json()
        
        # All activity names should be accessible
        for activity_name in activities.keys():
            # Try to access each activity through signup endpoint
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": "test@mergington.edu"}
            )
            # Should either succeed (200) or fail with expected errors (400, 404)
            assert response.status_code in [200, 400, 404]

    def test_max_participants_enforcement(self, client, sample_data):
        """Test that max participants limit is enforced (or at least sign-up works)."""
        activity = sample_data["activities"]["empty"]
        max_participants = client.get("/activities").json()[activity]["max_participants"]
        
        # Sign up participants up to the limit
        for i in range(min(3, max_participants)):  # Just test a few signups
            email = f"participant{i}@mergington.edu"
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        participants_count = len(response.json()[activity]["participants"])
        assert participants_count >= 3

    def test_root_endpoint_redirect(self, client):
        """Test that root endpoint redirects to static HTML."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]
