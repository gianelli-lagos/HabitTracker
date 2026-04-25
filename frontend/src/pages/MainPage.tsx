import { useEffect, useState } from "react";
import { 
  logoutUser, 
  getNotifications, 
  getUnreadCount, 
  markAsRead as markNotificationAsRead,
  uploadProfilePicture
} from "../api";
import type { Notification } from "../api";
import MyHabitsPage from "./MyHabitsPage";
import CalendarPage from "./CalendarPage";
import SocialPage from "./SocialPage";

interface MainPageProps {
  onLogout: () => void;
}

interface User {
  id: number;
  username: string;
  profile_picture_url?: string;
}

export default function MainPage({ onLogout }: MainPageProps) {
  const [username, setUsername] = useState("");
  const [profilePictureUrl, setProfilePictureUrl] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<"habits" | "notifications" | "events" | "social" | "profile">("habits");
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loadingNotifications, setLoadingNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false); 

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      fetch("/api/auth/profile", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data: User) => {
          setUsername(data.username);
          if (data.profile_picture_url) {
            setProfilePictureUrl(`/api${data.profile_picture_url}`);
          }
        })
        .catch(err => console.error("Profile fetch error:", err));
    }
  }, []);

  useEffect(() => {
    if (currentView === "notifications") {
      fetchNotifications();
    }
  }, [currentView]);

  useEffect(() => {
    async function fetchUnreadCountFromAPI() {
      try {
        const count = await getUnreadCount();
        setUnreadCount(count);
      } catch (error) {
        console.error("Failed to fetch unread count:", error);
      }
    }

    fetchUnreadCountFromAPI();
    const interval = setInterval(fetchUnreadCountFromAPI, 30000);
    return () => clearInterval(interval);
  }, []);

  async function fetchNotifications() {
    setLoadingNotifications(true);
    try {
      const data = await getNotifications();
      setNotifications(data);
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
    } finally {
      setLoadingNotifications(false);
    }
  }

  async function markAsRead(id: number) {
    try {
      await markNotificationAsRead(id);
      fetchNotifications();
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error("Failed to mark as read:", error);
    }
  }

  function handleLogout() {
    logoutUser();
    onLogout();
  }

  async function handleProfilePictureUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const result = await uploadProfilePicture(file);
      setProfilePictureUrl(`/api${result.profile_picture_url}`);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to upload profile picture");
    }
  }

  function getTimeAgo(timestamp: string): string {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  }

  function getNotificationIcon(type: string): string {
    switch (type) {
      case "milestone": return "🎉";
      case "habit_reminder": return "🌱";
      case "streak_broken": return "😔";
      case "event_1day": return "📅";
      case "event_1hour": return "🔔";
      case "weekly_summary": return "📊";
      case "test": return "🚀";
      default: return "🔔";
    }
  }

  return (
    <div className="layout">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="user-section">
          <div>
            <div className="user-name">{username}</div>
          </div>
        </div>

        <nav className="nav">
          <div 
            className={currentView === "habits" ? "nav-item-active" : "nav-item"} 
            onClick={() => setCurrentView("habits")}
          >
            🏠 My Habits
          </div>
          
          <div 
            className={currentView === "notifications" ? "nav-item-active" : "nav-item"} 
            onClick={() => setCurrentView("notifications")}
          >
            <span>🔔 Notifications</span>
            {unreadCount > 0 && (
              <span className="notification-badge">●</span>
            )}
          </div>
          
          <div
            className={currentView === "events" ? "nav-item-active" : "nav-item"}
            onClick={() => setCurrentView("events")}
          >
            📅 Events
          </div>
          <div 
            className={currentView === "social" ? "nav-item-active" : "nav-item"}
            onClick={() => setCurrentView("social")}
          >
            👥 Social
          </div>
          <div 
            className={currentView === "profile" ? "nav-item-active" : "nav-item"} 
            onClick={() => setCurrentView("profile")}
          >
            👤 Profile
          </div>
        </nav>
        <button className="logout-btn" onClick={handleLogout}>Log Out</button>
      </div>

      {/* Main Content */}
      <div className="main">
        {/* Top Banner */}
        <div className="top-banner">
          <div>
            <h1 className="page-title">
              {currentView === "habits" && "My Habits"}
              {currentView === "notifications" && "Notifications"}
              {currentView === "events" && "Events"}
              {currentView === "social" && "Social"}
              {currentView === "profile" && "Profile"}
            </h1>
            <p className="page-subtitle">
              {currentView === "habits" && "Track your progress and stay motivated"}
              {currentView === "notifications" && "Stay updated on your progress"}
              {currentView === "events" && "See and manage your calendar events"}
              {currentView === "social" && "Connect with friends and share your journey"}
              {currentView === "profile" && "Manage your account settings"}
            </p>
          </div>
        </div>

        <div className="content">
          {/* HABITS VIEW */}
          {currentView === "habits" && (
            <MyHabitsPage 
              externalOpenModal={isCreateModalOpen} 
              onModalClose={() => setIsCreateModalOpen(false)} 
            />
          )}
          
          {/* NOTIFICATIONS VIEW */}
          {currentView === "notifications" && (
            <>
              {loadingNotifications ? (
                <div className="placeholder">Loading notifications...</div>
              ) : notifications.length === 0 ? (
                <div className="empty-state-card">
                  <div className="empty-icon">🔔</div>
                  <h3 className="empty-title">No notifications yet</h3>
                  <p className="empty-text">We'll notify you when something important happens!</p>
                </div>
              ) : (
                <div className="notifications-container">
                  {notifications.map((notif) => (
                    <div
                      key={notif.id}
                      className={notif.is_read ? "notification-card" : "notification-card-unread"}
                      onClick={() => !notif.is_read && markAsRead(notif.id)}
                    >
                      <div className="notification-header">
                        <div className="notification-icon-large">
                          {getNotificationIcon(notif.type)}
                        </div>
                        <div className="notification-meta">
                          <div className="notification-time">{getTimeAgo(notif.created_at)}</div>
                          {!notif.is_read && <div className="unread-dot">●</div>}
                        </div>
                      </div>
                      <h3 className="notification-title">{notif.title}</h3>
                      <p className="notification-message">{notif.message}</p>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
          
          {/* PROFILE VIEW */}
          {currentView === "profile" && (
            <div className="profile-card">
              <div className="profile-top">
                <div className="profile-avatar" style={{
                  backgroundImage: profilePictureUrl ? `url(${profilePictureUrl})` : undefined,
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                  backgroundColor: profilePictureUrl ? "transparent" : "#f97316",
                  color: profilePictureUrl ? "transparent" : "white"
                }}>
                  {!profilePictureUrl && (username?.[0]?.toUpperCase() ?? "?")}
                </div>
                <div>
                  <h2 className="profile-name">{username}</h2>
                  <label style={{ display: "inline-block" }}>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleProfilePictureUpload}
                      style={{ display: "none" }}
                    />
                    <button 
                      className="change-pic-btn"
                      onClick={(e) => {
                        const input = (e.currentTarget.previousElementSibling as HTMLInputElement);
                        input?.click();
                      }}
                    >
                      Change Profile Picture
                    </button>
                  </label>
                </div>
              </div>
              <div className="profile-stats">
                <div className="stat">
                  <span style={{color: "#7C3AED", fontSize: "1.8rem", fontWeight: 700}}>0</span>
                  <p>Total Habits</p>
                </div>
                <div className="stat">
                  <span style={{color: "#22c55e", fontSize: "1.8rem", fontWeight: 700}}>0%</span>
                  <p>Success Rate</p>
                </div>
                <div className="stat">
                  <span style={{color: "#f97316", fontSize: "1.8rem", fontWeight: 700}}>0</span>
                  <p>Longest Streak</p>
                </div>
              </div>
            </div>
          )}

          {/* EVENTS VIEW */}
          {currentView === "events" && <CalendarPage />}

          {/* SOCIAL VIEW */}
          {currentView === "social" && <SocialPage />}
        </div>  
      </div>  
    </div>    
  );
}