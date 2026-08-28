"""
Endpoint tests using the Arrange-Act-Assert (AAA) testing pattern.

Each test follows the AAA pattern:
1. ARRANGE: Set up the test data and preconditions
2. ACT: Perform the action being tested
3. ASSERT: Verify the results
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, test_client):
        """Test that GET / redirects to /static/index.html"""
        # ARRANGE
        # TestClient is ready and configured
        
        # ACT
        response = test_client.get("/", follow_redirects=False)
        
        # ASSERT
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, test_client, fresh_activities):
        """Test that GET /activities returns all 9 activities with correct structure"""
        # ARRANGE
        # fresh_activities provides reset activities data
        expected_activity_names = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Club",
            "Basketball Club",
            "Art Club",
            "Drama Club",
            "Debate Club",
            "Science Club"
        ]
        
        # ACT
        response = test_client.get("/activities")
        activities = response.json()
        
        # ASSERT
        assert response.status_code == 200
        assert len(activities) == 9
        
        # Verify all activities are present
        for activity_name in expected_activity_names:
            assert activity_name in activities
        
        # Verify activity structure
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_includes_participants(self, test_client, fresh_activities):
        """Test that activities include correct participant counts"""
        # ARRANGE
        # Expected participants for specific activities
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        expected_programming_participants = ["emma@mergington.edu", "sophia@mergington.edu"]
        expected_empty_soccer = []
        
        # ACT
        response = test_client.get("/activities")
        activities = response.json()
        
        # ASSERT
        assert activities["Chess Club"]["participants"] == expected_chess_participants
        assert activities["Programming Class"]["participants"] == expected_programming_participants
        assert activities["Soccer Club"]["participants"] == expected_empty_soccer


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, test_client, fresh_activities):
        """Test successful signup for an activity"""
        # ARRANGE
        activity_name = "Soccer Club"
        email = "new_student@mergington.edu"
        
        # ACT
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
        
        # Verify student was actually added
        activities_response = test_client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

    def test_signup_invalid_activity_returns_404(self, test_client, fresh_activities):
        """Test signup fails with 404 for non-existent activity"""
        # ARRANGE
        invalid_activity = "Underwater Basket Weaving"
        email = "student@mergington.edu"
        
        # ACT
        response = test_client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_signed_up_returns_400(self, test_client, fresh_activities):
        """Test signup fails with 400 when student already signed up"""
        # ARRANGE
        activity_name = "Chess Club"
        # michael is already in Chess Club from fresh_activities
        already_signed_email = "michael@mergington.edu"
        
        # ACT
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": already_signed_email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_missing_email_parameter_returns_422(self, test_client, fresh_activities):
        """Test signup fails with 422 when email parameter is missing"""
        # ARRANGE
        activity_name = "Soccer Club"
        # No email parameter provided
        
        # ACT
        response = test_client.post(f"/activities/{activity_name}/signup")
        
        # ASSERT
        assert response.status_code == 422  # Unprocessable Entity - Pydantic validation
        assert "detail" in response.json()


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, test_client, fresh_activities):
        """Test successful unregister from an activity"""
        # ARRANGE
        activity_name = "Chess Club"
        # daniel is in Chess Club from fresh_activities
        email = "daniel@mergington.edu"
        
        # Verify student is signed up before unregistering
        activities_before = test_client.get("/activities").json()
        assert email in activities_before[activity_name]["participants"]
        
        # ACT
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]
        
        # Verify student was actually removed
        activities_after = test_client.get("/activities").json()
        assert email not in activities_after[activity_name]["participants"]

    def test_unregister_invalid_activity_returns_404(self, test_client, fresh_activities):
        """Test unregister fails with 404 for non-existent activity"""
        # ARRANGE
        invalid_activity = "Non-existent Activity"
        email = "student@mergington.edu"
        
        # ACT
        response = test_client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up_returns_400(self, test_client, fresh_activities):
        """Test unregister fails with 400 when student is not signed up"""
        # ARRANGE
        activity_name = "Soccer Club"  # Empty participants list
        email = "not_signed_up@mergington.edu"
        
        # ACT
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_missing_email_parameter_returns_422(self, test_client, fresh_activities):
        """Test unregister fails with 422 when email parameter is missing"""
        # ARRANGE
        activity_name = "Chess Club"
        # No email parameter provided
        
        # ACT
        response = test_client.delete(f"/activities/{activity_name}/unregister")
        
        # ASSERT
        assert response.status_code == 422  # Unprocessable Entity - Pydantic validation
        assert "detail" in response.json()


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flows"""

    def test_signup_then_unregister_flow(self, test_client, fresh_activities):
        """Test complete flow: signup a student, then unregister them"""
        # ARRANGE
        activity_name = "Basketball Club"
        email = "athlete@mergington.edu"
        
        # Initially empty
        initial_activities = test_client.get("/activities").json()
        assert email not in initial_activities[activity_name]["participants"]
        
        # ACT - SIGNUP
        signup_response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT - SIGNUP SUCCESS
        assert signup_response.status_code == 200
        after_signup = test_client.get("/activities").json()
        assert email in after_signup[activity_name]["participants"]
        
        # ACT - UNREGISTER
        unregister_response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT - UNREGISTER SUCCESS
        assert unregister_response.status_code == 200
        after_unregister = test_client.get("/activities").json()
        assert email not in after_unregister[activity_name]["participants"]

    def test_multiple_students_signup_to_same_activity(self, test_client, fresh_activities):
        """Test multiple students can sign up to the same activity"""
        # ARRANGE
        activity_name = "Art Club"
        student1 = "alice@mergington.edu"
        student2 = "bob@mergington.edu"
        
        # ACT - First signup
        response1 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student1}
        )
        
        # ACT - Second signup
        response2 = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student2}
        )
        
        # ASSERT
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = test_client.get("/activities").json()
        assert student1 in activities[activity_name]["participants"]
        assert student2 in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 2
