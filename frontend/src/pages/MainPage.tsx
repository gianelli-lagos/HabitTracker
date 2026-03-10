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
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.avatar}>{username?.[0]?.toUpperCase() ?? "?"}</div>
        <h2 style={styles.username}>{username}</h2>
        <p style={styles.placeholder}>🖼️ Profile picture coming soon</p>
        <button style={styles.logoutBtn} onClick={handleLogout}>Log Out</button>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "#F5F3FF" },
  card: { backgroundColor: "#fff", padding: "2.5rem", borderRadius: "12px", boxShadow: "0 4px 20px rgba(0,0,0,0.1)", textAlign: "center" as const, width: "90%", maxWidth: "400px" },
  avatar: { width: "80px", height: "80px", borderRadius: "50%", backgroundColor: "#7C3AED", color: "#fff", fontSize: "2rem", fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1rem" },
  username: { fontSize: "1.5rem", marginBottom: "0.5rem" },
  placeholder: { color: "#aaa", marginBottom: "1.5rem" },
  logoutBtn: { padding: "0.6rem 1.5rem", backgroundColor: "#e53935", color: "#fff", border: "none", borderRadius: "8px", cursor: "pointer", fontWeight: 600 },
};