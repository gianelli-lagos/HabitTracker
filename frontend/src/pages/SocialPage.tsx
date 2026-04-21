import { useEffect, useState } from "react";
import {
  sendFriendRequest,
  getPendingRequests,
  acceptFriendRequest,
  rejectFriendRequest,
  getFriends,
  searchUsers,
} from "../api";
import type {
  Friend,
  PendingRequest,
  SearchUser,
} from "../api";

export default function SocialPage() {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [pendingRequests, setPendingRequests] = useState<PendingRequest[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Fetch pending requests and friends on mount
  useEffect(() => {
    fetchData();
  }, []);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery.trim()) {
        performSearch();
      } else {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

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

  async function performSearch() {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setSearching(true);
      setError("");
      const results = await searchUsers(searchQuery);
      setSearchResults(results);
    } catch (err) {
      console.error("Search failed:", err);
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  }

  async function handleSendRequest(username: string) {
    if (!username.trim()) return;

    try {
      setError("");
      setMessage("");
      await sendFriendRequest(username);
      setMessage(`Friend request sent to ${username}!`);
      setSearchQuery("");
      setSearchResults([]);
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
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by username..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>

        {searching && <p className="loading-text">Searching...</p>}

        {searchResults.length > 0 && (
          <div className="search-results">
            {searchResults.map((user) => (
              <div key={user.id} className="search-result-item">
                <div className="result-avatar" style={{
                  backgroundImage: user.profile_picture_url 
                    ? `url(http://localhost:8000${user.profile_picture_url})` 
                    : undefined,
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                  color: user.profile_picture_url ? "transparent" : "white"
                }}>
                  {!user.profile_picture_url && user.username?.[0]?.toUpperCase()}
                </div>
                <div className="result-info">
                  <p className="result-username">{user.username}</p>
                </div>
                <button
                  onClick={() => handleSendRequest(user.username)}
                  className="btn-add-friend"
                >
                  Add
                </button>
              </div>
            ))}
          </div>
        )}

        {searchQuery.trim() && searchResults.length === 0 && !searching && (
          <p className="empty-text">No users found matching "{searchQuery}"</p>
        )}

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
