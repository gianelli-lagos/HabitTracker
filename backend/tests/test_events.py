"""
Tests for Event endpoints, especially invite features
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from main import app
from database import get_db
from sqlalchemy.orm import Session
from tests.conftest import TestingSessionLocal
from models.event import Event, EventAttendee

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


class TestEventCreate:
    """Tests for creating events"""
    
    def test_create_event_without_invites(self, test_user, db):
        """User can create event without inviting anyone"""
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        response = client.post(
            "/events",
            json={
                "title": "Team Meeting",
                "description": "Quarterly review",
                "start_time": start_time,
                "end_time": end_time,
                "location": "Conference Room A",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Team Meeting"
        assert data["description"] == "Quarterly review"
        assert data["location"] == "Conference Room A"
        assert data["creator_id"] == test_user.id
        
    def test_create_event_with_invites(self, test_user, test_user2, test_user3, db):
        """User can create event and invite multiple friends"""
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=2)).isoformat()
        end_time = (datetime.now() + timedelta(days=2, hours=2)).isoformat()
        
        response = client.post(
            "/events",
            json={
                "title": "Project Kickoff",
                "description": "New project discussion",
                "start_time": start_time,
                "end_time": end_time,
                "location": "Virtual - Zoom",
                "invite_user_ids": [test_user2.id, test_user3.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        event_data = response.json()
        event_id = event_data["id"]
        
        # Verify attendees were created
        attendees = event_data.get("attendees", [])
        assert len(attendees) == 2
        assert all(a["status"] == "invited" for a in attendees)
        attendee_ids = {a["user_id"] for a in attendees}
        assert test_user2.id in attendee_ids
        assert test_user3.id in attendee_ids
    
    def test_create_event_invalid_time_range(self, test_user, db):
        """Creating event with end_time <= start_time fails"""
        token = get_token("testuser")
        start_time = datetime.now().isoformat()
        end_time = (datetime.now() - timedelta(hours=1)).isoformat()
        
        response = client.post(
            "/events",
            json={
                "title": "Invalid Event",
                "start_time": start_time,
                "end_time": end_time,
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "end_time must be after start_time" in response.json()["detail"]


class TestEventInvites:
    """Tests for updating event invites"""
    
    def test_update_event_invites_add_friends(self, test_user, test_user2, test_user3, db):
        """Creator can add friends to existing event"""
        # Create event without invites
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Team Sync",
                "start_time": start_time,
                "end_time": end_time,
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        # Add invites
        response = client.put(
            f"/events/{event_id}/invites",
            json={"user_ids": [test_user2.id, test_user3.id]},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["added"]) == 2
        assert len(data["removed"]) == 0
        assert test_user2.id in data["added"]
        assert test_user3.id in data["added"]
    
    def test_update_event_invites_remove_friends(self, test_user, test_user2, test_user3, db):
        """Creator can remove friends from event"""
        # Create event with 2 invites
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Team Meeting",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id, test_user3.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        # Remove one friend (keep only test_user2)
        response = client.put(
            f"/events/{event_id}/invites",
            json={"user_ids": [test_user2.id]},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["removed"]) == 1
        assert test_user3.id in data["removed"]
        
    def test_update_event_invites_keep_status(self, test_user, test_user2, test_user3, db):
        """Updating invites preserves existing attendee status"""
        # Create event with 2 invites
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Event",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id, test_user3.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        # test_user2 accepts
        token2 = get_token("testuser2")
        client.put(
            f"/events/{event_id}/respond",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # Update invites - keep all users
        response = client.put(
            f"/events/{event_id}/invites",
            json={"user_ids": [test_user2.id, test_user3.id]},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Get updated event
        event_response = client.get(
            f"/events/{event_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        event = event_response.json()
        
        # test_user2 should still have accepted status
        attendee2 = next(a for a in event["attendees"] if a["user_id"] == test_user2.id)
        assert attendee2["status"] == "accepted"
    
    def test_update_event_invites_not_creator(self, test_user, test_user2, test_user3, db):
        """Only creator can update invites"""
        # Create event as test_user
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Event",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        # test_user2 tries to update invites
        token2 = get_token("testuser2")
        response = client.put(
            f"/events/{event_id}/invites",
            json={"user_ids": [test_user3.id]},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 403
        assert "Only the creator can update invites" in response.json()["detail"]


class TestEventRespond:
    """Tests for responding to event invitations"""
    
    def test_accept_event_invitation(self, test_user, test_user2, db):
        """Invited user can accept event invitation"""
        # Create event with test_user2 invited
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Conference",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        # test_user2 accepts
        token2 = get_token("testuser2")
        response = client.put(
            f"/events/{event_id}/respond",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"
        assert response.json()["responded_at"] is not None
    
    def test_decline_event_invitation(self, test_user, test_user2, db):
        """Invited user can decline event invitation"""
        # Create event with test_user2 invited
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Conference",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        # test_user2 declines
        token2 = get_token("testuser2")
        response = client.put(
            f"/events/{event_id}/respond",
            json={"status": "declined"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "declined"
    
    def test_respond_invalid_status(self, test_user, test_user2, db):
        """Invalid status response is rejected"""
        # Create event
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Event",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        # test_user2 tries invalid status
        token2 = get_token("testuser2")
        response = client.put(
            f"/events/{event_id}/respond",
            json={"status": "maybe"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 400
        assert "status must be 'accepted' or 'declined'" in response.json()["detail"]
    
    def test_respond_not_invited(self, test_user, test_user2, test_user3, db):
        """User not invited to event cannot respond"""
        # Create event with test_user2 invited (not test_user3)
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Event",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        # test_user3 tries to respond (not invited)
        token3 = get_token("testuser3")
        response = client.put(
            f"/events/{event_id}/respond",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {token3}"}
        )
        
        assert response.status_code == 404
        assert "Invitation not found" in response.json()["detail"]


class TestEventRetrieval:
    """Tests for retrieving events with proper attendee information"""
    
    def test_get_events_includes_attendees(self, test_user, test_user2, test_user3, db):
        """Events returned include full attendee information with usernames"""
        # Create event with invites
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Team Lunch",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id, test_user3.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        # Have test_user2 accept
        token2 = get_token("testuser2")
        client.put(
            f"/events/{event_id}/respond",
            json={"status": "accepted"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # Retrieve events
        response = client.get(
            "/events",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        events = response.json()
        event = next(e for e in events if e["id"] == event_id)
        
        assert len(event["attendees"]) == 2
        
        # Check attendee with username info
        user2_attendee = next(a for a in event["attendees"] if a["user_id"] == test_user2.id)
        assert user2_attendee["user"]["username"] == "testuser2"
        assert user2_attendee["status"] == "accepted"
        
        user3_attendee = next(a for a in event["attendees"] if a["user_id"] == test_user3.id)
        assert user3_attendee["user"]["username"] == "testuser3"
        assert user3_attendee["status"] == "invited"
    
    def test_get_created_events(self, test_user, test_user2, db):
        """User can retrieve events they created"""
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        # Create 2 events
        client.post(
            "/events",
            json={
                "title": "Event 1",
                "start_time": start_time,
                "end_time": end_time,
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        client.post(
            "/events",
            json={
                "title": "Event 2",
                "start_time": start_time,
                "end_time": end_time,
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = client.get(
            "/events",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        events = response.json()
        assert len(events) == 2
        assert all(e["creator_id"] == test_user.id for e in events)
    
    def test_get_invited_events(self, test_user, test_user2, db):
        """User can retrieve events they are invited to"""
        # test_user creates event and invites test_user2
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        client.post(
            "/events",
            json={
                "title": "Invited Event",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # test_user2 retrieves events
        token2 = get_token("testuser2")
        response = client.get(
            "/events",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        events = response.json()
        assert len(events) == 1
        assert events[0]["title"] == "Invited Event"
        assert events[0]["creator_id"] == test_user.id


class TestEventAccess:
    """Tests for event access control"""
    
    def test_creator_can_view_event(self, test_user, db):
        """Creator can view their event"""
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "My Event",
                "start_time": start_time,
                "end_time": end_time,
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        response = client.get(
            f"/events/{event_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["title"] == "My Event"
    
    def test_invited_user_can_view_event(self, test_user, test_user2, db):
        """Invited user can view event"""
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Group Event",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        token2 = get_token("testuser2")
        response = client.get(
            f"/events/{event_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 200
        assert response.json()["title"] == "Group Event"
    
    def test_non_invited_cannot_view_event(self, test_user, test_user2, test_user3, db):
        """Non-invited user cannot view event"""
        token = get_token("testuser")
        start_time = (datetime.now() + timedelta(days=1)).isoformat()
        end_time = (datetime.now() + timedelta(days=1, hours=1)).isoformat()
        
        create_response = client.post(
            "/events",
            json={
                "title": "Private Event",
                "start_time": start_time,
                "end_time": end_time,
                "invite_user_ids": [test_user2.id],
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        event_id = create_response.json()["id"]
        
        # test_user3 tries to view (not invited)
        token3 = get_token("testuser3")
        response = client.get(
            f"/events/{event_id}",
            headers={"Authorization": f"Bearer {token3}"}
        )
        
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
