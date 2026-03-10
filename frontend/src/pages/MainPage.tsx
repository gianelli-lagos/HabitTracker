import { useEffect, useState } from "react";
import { logoutUser } from "../api";

interface MainPageProps {
  onLogout: () => void;
}

interface User {
  id: number;
  username: string;
}

export default function MainPage({ onLogout }: MainPageProps) {
  const [username, setUsername] = useState("");
  const [currentView, setCurrentView] = useState<"habits" | "profile">("habits");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      fetch("http://localhost:8000/auth/profile", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data: User) => setUsername(data.username));
    }
  }, []);

  function handleLogout() {
    logoutUser();
    onLogout();
  }

  return (
    <div style={styles.layout}>
      {/* Sidebar */}
      <div style={styles.sidebar}>
        <div style={styles.logoSection}>
          <span style={styles.logoIcon}>🌱</span>
          <div>
            <div style={styles.logoText}>HabitFlow</div>
            <div style={styles.logoSub}>Build better habits</div>
          </div>
        </div>
        <div style={styles.userSection}>
          <div style={styles.avatar}>{username?.[0]?.toUpperCase() ?? "?"}</div>
          <div>
            <div style={styles.userName}>{username}</div>
          </div>
        </div>
        <nav style={styles.nav}>
          <div style={currentView === "habits" ? styles.navItemActive : styles.navItem} onClick={() => setCurrentView("habits")}>🏠 My Habits</div>
          <div style={styles.navItem}>📅 Events</div>
          <div style={styles.navItem}>👥Social</div>
         <div style={currentView === "profile" ? styles.navItemActive : styles.navItem} onClick={() => setCurrentView("profile")}>👤 Profile</div>
        </nav>
        <button style={styles.newHabitBtn}>+ New Habit</button>
        <button style={styles.logoutBtn} onClick={handleLogout}>Log Out</button>
      </div>

      {/* Main Content */}
      <div style={styles.main}>
        {/* Top Banner */}
        <div style={styles.topBanner}>
          <div>
            <h1 style={styles.pageTitle}>My Habits</h1>
            <p style={styles.pageSubtitle}>Track your progress and stay motivated</p>
          </div>
        </div>

    <div style={styles.content}>
    {currentView === "habits" ? (
        <>
        <p style={styles.placeholder}>Habit Tracking</p>
        <p style={styles.placeholder}>Calendar Heatmap</p>
        <p style={styles.placeholder}>Milestones</p>
        </>
    ) : (
        <div style={styles.profileCard}>
        <div style={styles.profileTop}>
            <div style={styles.profileAvatar}>{username?.[0]?.toUpperCase() ?? "?"}</div>
            <div>
            <h2 style={styles.profileName}>{username}</h2>
            <button style={styles.changePicBtn}>Change Profile Picture</button>
            </div>
        </div>
        <div style={styles.profileStats}>
            <div style={styles.stat}><span style={{color: "#7C3AED", fontSize: "1.8rem", fontWeight: 700}}>0</span><p>Total Habits</p></div>
            <div style={styles.stat}><span style={{color: "#22c55e", fontSize: "1.8rem", fontWeight: 700}}>0%</span><p>Success Rate</p></div>
            <div style={styles.stat}><span style={{color: "#f97316", fontSize: "1.8rem", fontWeight: 700}}>0</span><p>Longest Streak</p></div>
        </div>
        </div>
    )}
    </div>  
      </div>  
    </div>    
  );
}

const styles: Record<string, React.CSSProperties> = {
  layout: { display: "flex", minHeight: "100vh", fontFamily: "sans-serif" },
  sidebar: { width: "240px", backgroundColor: "#fff", borderRight: "1px solid #eee", display: "flex", flexDirection: "column" as const, padding: "1.5rem 1rem", gap: "1.5rem" },
  logoSection: { display: "flex", alignItems: "center", gap: "0.75rem" },
  logoIcon: { fontSize: "2rem" },
  logoText: { fontWeight: 700, fontSize: "1.1rem" },
  logoSub: { fontSize: "0.75rem", color: "#888" },
  userSection: { display: "flex", alignItems: "center", gap: "0.75rem", backgroundColor: "#F5F3FF", borderRadius: "8px", padding: "0.75rem" },
  avatar: { width: "40px", height: "40px", borderRadius: "50%", backgroundColor: "#7C3AED", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: "1rem" },
  userName: { fontWeight: 600, fontSize: "0.9rem" },
  nav: { display: "flex", flexDirection: "column" as const, gap: "0.25rem", flex: 1 },
  navItem: { padding: "0.6rem 0.75rem", borderRadius: "8px", cursor: "pointer", color: "#555", fontSize: "0.95rem" },
  navItemActive: { padding: "0.6rem 0.75rem", borderRadius: "8px", cursor: "pointer", backgroundColor: "#F5F3FF", color: "#7C3AED", fontWeight: 600, fontSize: "0.95rem" },
  newHabitBtn: { padding: "0.75rem", backgroundColor: "#7C3AED", color: "#fff", border: "none", borderRadius: "8px", cursor: "pointer", fontWeight: 600, fontSize: "0.95rem" },
  main: { flex: 1, backgroundColor: "#F9FAFB", display: "flex", flexDirection: "column" as const },
  topBanner: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "1.5rem 2rem", backgroundColor: "#fff", borderBottom: "1px solid #eee" },
  pageTitle: { fontSize: "1.5rem", fontWeight: 700, margin: 0 },
  pageSubtitle: { color: "#888", margin: 0, fontSize: "0.9rem" },
  logoutBtn: { padding: "0.5rem 1rem", backgroundColor: "#e53935", color: "#fff", border: "none", borderRadius: "8px", cursor: "pointer", fontWeight: 600 },
  content: { padding: "2rem", display: "flex", flexDirection: "column" as const, gap: "1rem" },
  placeholder: { backgroundColor: "#fff", padding: "1.5rem", borderRadius: "8px", color: "#7C3AED", boxShadow: "0 2px 8px rgba(0,0,0,0.05)" },
  profileCard: { backgroundColor: "#fff", borderRadius: "12px", padding: "2rem", boxShadow: "0 2px 8px rgba(0,0,0,0.05)" },
  profileTop: { display: "flex", alignItems: "center", gap: "1.5rem", marginBottom: "2rem" },
  profileAvatar: { width: "80px", height: "80px", borderRadius: "50%", backgroundColor: "#f97316", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "2rem", fontWeight: 700 },
  profileName: { fontSize: "1.5rem", fontWeight: 700, margin: "0 0 0.5rem" },
  changePicBtn: { padding: "0.4rem 1rem", border: "1px solid #ddd", borderRadius: "8px", cursor: "pointer", backgroundColor: "#fff" },
  profileStats: { display: "flex", gap: "2rem", borderTop: "1px solid #eee", paddingTop: "1.5rem" },
  stat: { textAlign: "center" as const, color: "#888", fontSize: "0.9rem" },
};