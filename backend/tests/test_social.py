"""
Tests for Social/Friendship endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db
from sqlalchemy.orm import Session
from tests.conftest import TestingSessionLocal

# Override dependency to use test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def get_token(username: str, password: str = "test123"):
    """Helper to login and get JWT token"""
    formData = {
        "username": username,
        "password": password,
    }
    response = client.post("/auth/login", data=formData)
    return response.json()["access_token"]

class TestFriendRequest:
    """Tests for sending friend requests"""
    
    def test_send_friend_request_success(self, test_user, test_user2, db):
        """User can send friend request to another user"""
        token = get_token("testuser")
        
        response = client.post(
            "/social/friend-request",
            json={"username": "testuser2"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Friend request sent"
        assert response.json()["request_id"] is not None
    
    def test_send_friend_request_user_not_found(self, test_user, db):
        """Sending request to non-existent user fails"""
        token = get_token("testuser")
        
        response = client.post(
            "/social/friend-request",
            json={"username": "nonexistent"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_send_friend_request_to_self_fails(self, test_user, db):
        """Cannot send friend request to yourself"""
        token = get_token("testuser")
        
        response = client.post(
            "/social/friend-request",
            json={"username": "testuser"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "Cannot send request to yourself" in response.json()["detail"]
    
    def test_send_duplicate_friend_request_fails(self, test_user, test_user2, db):
        """Cannot send duplicate friend request"""
        token = get_token("testuser")
        
        # First request succeeds
        response1 = client.post(
            "/social/friend-request",
            json={"username": "testuser2"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 200
        
        # Second request fails
        response2 = client.post(
            "/social/friend-request",
            json={"username": "testuser2"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response2.status_code == 400
        assert "Friend request already exists" in response2.json()["detail"]

class TestPendingRequests:
    """Tests for viewing pending requests"""
    
    def test_get_pending_requests_empty(self, test_user, db):
        """User with no pending requests gets empty list"""
        token = get_token("testuser")
        
        response = client.get(
            "/social/pending-requests",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_pending_requests(self, test_user, test_user2, db):
        """User sees pending requests sent to them"""
        # User2 sends request to User1
        token2 = get_token("testuser2")
        client.post(
            "/social/friend-request",
            json={"username": "testuser"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # User1 checks pending requests
        token1 = get_token("testuser")
        response = client.get(
            "/social/pending-requests",
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sender"]["username"] == "testuser2"
        assert "created_at" in data[0]

class TestAcceptRequest:
    """Tests for accepting friend requests"""
    
    def test_accept_friend_request_success(self, test_user, test_user2, db):
        """User can accept pending request"""
        # User2 sends request to User1
        token2 = get_token("testuser2")
        response_send = client.post(
            "/social/friend-request",
            json={"username": "testuser"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        request_id = response_send.json()["request_id"]
        
        # User1 accepts
        token1 = get_token("testuser")
        response = client.post(
            f"/social/friend-request/{request_id}/accept",
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Friend request accepted"
    
    def test_accept_nonexistent_request(self, test_user, db):
        """Cannot accept request that doesn't exist"""
        token = get_token("testuser")
        
        response = client.post(
            "/social/friend-request/999/accept",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "Friend request not found" in response.json()["detail"]

class TestRejectRequest:
    """Tests for rejecting friend requests"""
    
    def test_reject_friend_request_success(self, test_user, test_user2, db):
        """User can reject pending request"""
        # User2 sends request to User1
        token2 = get_token("testuser2")
        response_send = client.post(
            "/social/friend-request",
            json={"username": "testuser"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        request_id = response_send.json()["request_id"]
        
        # User1 rejects
        token1 = get_token("testuser")
        response = client.post(
            f"/social/friend-request/{request_id}/reject",
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Friend request declined"

class TestFriendsList:
    """Tests for getting friends list"""
    
    def test_get_friends_empty(self, test_user, db):
        """User with no friends gets empty list"""
        token = get_token("testuser")
        
        response = client.get(
            "/social/friends",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_friends_after_accept(self, test_user, test_user2, db):
        """Friends list includes accepted requests (both directions)"""
        # User1 sends request to User2
        token1 = get_token("testuser")
        response_send = client.post(
            "/social/friend-request",
            json={"username": "testuser2"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        request_id = response_send.json()["request_id"]
        
        # User2 accepts
        token2 = get_token("testuser2")
        client.post(
            f"/social/friend-request/{request_id}/accept",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # User1 sees User2 in friends list
        response1 = client.get(
            "/social/friends",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert len(response1.json()) == 1
        assert response1.json()[0]["username"] == "testuser2"
        
        # User2 sees User1 in friends list
        response2 = client.get(
            "/social/friends",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert len(response2.json()) == 1
        assert response2.json()[0]["username"] == "testuser"
    
    def test_get_friends_multiple(self, test_user, test_user2, test_user3, db):
        """User can have multiple friends"""
        token1 = get_token("testuser")
        token2 = get_token("testuser2")
        token3 = get_token("testuser3")
        
        # User1 sends requests to User2 and User3
        resp2 = client.post(
            "/social/friend-request",
            json={"username": "testuser2"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        req_id2 = resp2.json()["request_id"]
        
        resp3 = client.post(
            "/social/friend-request",
            json={"username": "testuser3"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        req_id3 = resp3.json()["request_id"]
        
        # User2 and User3 accept
        client.post(
            f"/social/friend-request/{req_id2}/accept",
            headers={"Authorization": f"Bearer {token2}"}
        )
        client.post(
            f"/social/friend-request/{req_id3}/accept",
            headers={"Authorization": f"Bearer {token3}"}
        )
        
        # User1 has 2 friends
        response = client.get(
            "/social/friends",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert len(response.json()) == 2
        usernames = [f["username"] for f in response.json()]
        assert "testuser2" in usernames
        assert "testuser3" in usernames
