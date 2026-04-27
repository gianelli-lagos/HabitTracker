import { useState } from "react";
import { isLoggedIn } from "./api";
import AuthPage from "./pages/AuthPage";
import MainPage from "./pages/MainPage";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(isLoggedIn());

  if (!loggedIn) {
    return <AuthPage onLoginSuccess={() => setLoggedIn(true)} />;
  }

  return (
    <div>
      <nav style={styles.nav}>
        <span style={styles.brand}>🌱 HabitTracker</span>
      </nav>
      <MainPage onLogout={() => setLoggedIn(false)} />
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  nav: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "1rem 2rem", backgroundColor: "#7C3AED" },
  brand: { fontSize: "1.2rem", fontWeight: 700, color: "#fff" },
};