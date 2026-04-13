import { useEffect, useState } from "react";
import { 
  logoutUser, 
  getNotifications, 
  getUnreadCount, 
  markAsRead as markNotificationAsRead 
} from "../api";
import type { Notification } from "../api";
import MyHabitsPage from "./MyHabitsPage";

interface MainPageProps {
  onLogout: () => void;
}

interface User {
  id: number;
  username: string;
}

export default function MainPage({ onLogout }: MainPageProps) {
  const [username, setUsername] = useState("");
  const [currentView, setCurrentView] = useState<"habits" | "notifications" | "profile">("habits");
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loadingNotifications, setLoadingNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  
  // State to bridge the Sidebar button and the MyHabitsPage modal
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false); 

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      fetch("http://localhost:8000/auth/profile", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data: User) => setUsername(data.username))
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
        <div className="logo-section">
          <span className="logo-icon">🌱</span>
          <div>
            <div className="logo-text">HabitFlow</div>
            <div className="logo-sub">Build better habits</div>
          </div>
        </div>
        
        <div className="user-section">
          <div className="avatar">{username?.[0]?.toUpperCase() ?? "?"}</div>
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
          
          <div className="nav-item">📅 Events</div>
          <div className="nav-item">👥 Social</div>
          <div 
            className={currentView === "profile" ? "nav-item-active" : "nav-item"} 
            onClick={() => setCurrentView("profile")}
          >
            👤 Profile
          </div>
        </nav>

        {/* Action Buttons */}
        <button 
          className="new-habit-btn" 
          onClick={() => {
            setCurrentView("habits");
            setIsCreateModalOpen(true);
          }}
        >
          + New Habit
        </button>
        
        <button className="logout-btn" onClick={handleLogout}>Log Out</button>
      </div>

      {/* Main Content Area */}
      <div className="main">
        {/* Top Banner */}
        <div className="top-banner">
          <div>
            <h1 className="page-title">
              {currentView === "habits" && "My Habits"}
              {currentView === "notifications" && "Notifications"}
              {currentView === "profile" && "Profile"}
            </h1>
            <p className="page-subtitle">
              {currentView === "habits" && "Track your progress and stay motivated"}
              {currentView === "notifications" && "Stay updated on your progress"}
              {currentView === "profile" && "Manage your account settings"}
            </p>
          </div>
        </div>
        <div className="content">
          {currentView === "habits" && <MyHabitsPage />}
          
          {/* Keep your other views (notifications/profile) as they were */}
        </div>
      </div>  
    </div>    
  );
}