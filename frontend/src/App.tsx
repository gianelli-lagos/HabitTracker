import { useState } from "react";
import { isLoggedIn } from "./api";
import AuthPage from "./pages/AuthPage";
import MainPage from "./pages/MainPage";
import UserHabits from "./pages/UserHabits";
import MyHabitsPage from "./pages/MyHabitsPage";

type Page = "main" | "habits";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(isLoggedIn());
  const [currentPage, setCurrentPage] = useState<Page>("main");

  if (!loggedIn) {
    return <AuthPage onLoginSuccess={() => setLoggedIn(true)} />;
  }

  return (
    <div>
      <nav style={styles.nav}>
        <span style={styles.brand}>🌱 HabitFlow</span>
        <div style={styles.navLinks}>
          <button style={currentPage === "main" ? styles.navBtnActive : styles.navBtn} onClick={() => setCurrentPage("main")}>Profile</button>
          <button style={currentPage === "habits" ? styles.navBtnActive : styles.navBtn} onClick={() => setCurrentPage("habits")}>My Habits</button>
        </div>
      </nav>
      {currentPage === "main" ? <MainPage onLogout={() => setLoggedIn(false)} /> : <MyHabitsPage />}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  nav: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "1rem 2rem", backgroundColor: "#7C3AED" },
  brand: { fontSize: "1.2rem", fontWeight: 700, color: "#fff" },
  navLinks: { display: "flex", gap: "0.5rem" },
  navBtn: { padding: "0.5rem 1rem", border: "none", borderRadius: "8px", cursor: "pointer", backgroundColor: "transparent", color: "#fff", fontWeight: 500 },
  navBtnActive: { padding: "0.5rem 1rem", border: "none", borderRadius: "8px", cursor: "pointer", backgroundColor: "#fff", color: "#7C3AED", fontWeight: 600 },
};