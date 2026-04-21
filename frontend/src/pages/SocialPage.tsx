import { useEffect, useState } from "react";
import {
  sendFriendRequest,
  getPendingRequests,
  acceptFriendRequest,
  rejectFriendRequest,
  getFriends,
  Friend,
  PendingRequest,
} from "../api";

export default function SocialPage() {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [pendingRequests, setPendingRequests] = useState<PendingRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [usernameInput, setUsernameInput] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Fetch pending requests and friends on mount
  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    try {
      setLoading(true);
      const [requests, friendsList] = await Promise.all([
        getPendingRequests(),
        getFriends(),
      ]);
      setPendingRequests(requests);
      setFriends(friendsList);
    } catch (err) {
      console.error("Failed to fetch social data:", err);
      setError("Failed to load social data");
    } finally {
      setLoading(false);
    }
  }

  async function handleSendRequest(e: React.FormEvent) {
    e.preventDefault();
    if (!usernameInput.trim()) return;

    try {
      setError("");
      setMessage("");
      await sendFriendRequest(usernameInput);
      setMessage(`Friend request sent to ${usernameInput}!`);
      setUsernameInput("");
      // Optionally refresh (request will show as pending on their end)
    } catch (err) {
      const errMsg = (err as Error).message;
      setError(errMsg);
    }
  }

  async function handleAccept(requestId: number) {
    try {
      setError("");
      await acceptFriendRequest(requestId);
      setMessage("Friend request accepted!");
      await fetchData(); // Refresh to update lists
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleReject(requestId: number) {
    try {
      setError("");
      await rejectFriendRequest(requestId);
      setMessage("Friend request rejected");
      await fetchData(); // Refresh
    } catch (err) {
      setError((err as Error).message);
    }
  }

  if (loading) {
    return <div className="placeholder">Loading social data...</div>;
  }

  return (
    <div className="social-container">
      {/* Add Friend Section */}
      <div className="social-card">
        <h3 className="social-card-title">Add Friend</h3>
        <form onSubmit={handleSendRequest} className="friend-form">
          <div className="form-group">
            <input
              type="text"
              placeholder="Enter username..."
              value={usernameInput}
              onChange={(e) => setUsernameInput(e.target.value)}
              className="friend-input"
            />
            <button type="submit" className="friend-btn">
              Send Request
            </button>
          </div>
        </form>
        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}
      </div>

      {/* Pending Invitations Section */}
      <div className="social-card">
        <h3 className="social-card-title">Pending Invitations</h3>
        {pendingRequests.length === 0 ? (
          <p className="empty-text">No pending invitations</p>
        ) : (
          <div className="pending-list">
            {pendingRequests.map((req) => (
              <div key={req.id} className="pending-item">
                <div className="pending-header">
                  <div className="pending-avatar" style={{
                    backgroundImage: req.sender.profile_picture_url 
                      ? `url(http://localhost:8000${req.sender.profile_picture_url})` 
                      : undefined,
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                    color: req.sender.profile_picture_url ? "transparent" : "white"
                  }}>
                    {!req.sender.profile_picture_url && req.sender.username?.[0]?.toUpperCase()}
                  </div>
                  <div className="pending-info">
                    <p className="pending-username">{req.sender.username}</p>
                    <p className="pending-time">
                      {new Date(req.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="pending-actions">
                  <button
                    onClick={() => handleAccept(req.id)}
                    className="btn-accept"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => handleReject(req.id)}
                    className="btn-reject"
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Friends List Section */}
      <div className="social-card">
        <h3 className="social-card-title">Friends ({friends.length})</h3>
        {friends.length === 0 ? (
          <p className="empty-text">You don't have any friends yet</p>
        ) : (
          <div className="friends-list">
            {friends.map((friend) => (
              <div key={friend.id} className="friend-item">
                <div className="friend-avatar" style={{
                  backgroundImage: friend.profile_picture_url
                    ? `url(http://localhost:8000${friend.profile_picture_url})`
                    : undefined,
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                  color: friend.profile_picture_url ? "transparent" : "white"
                }}>
                  {!friend.profile_picture_url && friend.username?.[0]?.toUpperCase()}
                </div>
                <div className="friend-info">
                  <p className="friend-username">{friend.username}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
