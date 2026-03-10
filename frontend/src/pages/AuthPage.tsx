import { useState } from "react";
import { loginUser, registerUser } from "../api";

interface AuthPageProps {
  onLoginSuccess: () => void;
}

export default function AuthPage({ onLoginSuccess }: AuthPageProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);


async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "register") {
        await registerUser(username, password);
        await loginUser(username, password);
      } else {
        await loginUser(username, password);
      }
      onLoginSuccess();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }
return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.logo}>🌱 HabitFlow</h1>
        <p style={styles.tagline}>Build better habits</p>
        <h2 style={styles.title}>
          {mode === "login" ? "Welcome back" : "Create account"}
        </h2>

        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            style={styles.input}
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            style={styles.input}
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <p style={styles.error}>{error}</p>}

          <button style={styles.button} type="submit" disabled={loading}>
            {loading ? "Loading..." : mode === "login" ? "Log In" : "Register"}
          </button>
        </form>

        <p style={styles.switchText}>
          {mode === "login" ? "Don't have an account? " : "Already have an account? "}
          <span style={styles.switchLink} onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
            {mode === "login" ? "Register" : "Log In"}
          </span>
        </p>
      </div>
    </div>
  );
}
const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#F5F3FF",
  },
  card: {
    backgroundColor: "#fff",
    padding: "2.5rem",
    borderRadius: "12px",
    boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
    width: "100%",
    maxWidth: "400px",
    textAlign: "center" as const,
  },
  logo: { fontSize: "1.8rem", marginBottom: "0" },
  tagline: { color: "#7C3AED", marginTop: "0", marginBottom: "1.5rem" },
  title: { fontWeight: 400, color: "#333", marginBottom: "1.5rem" },
  form: { display: "flex", flexDirection: "column" as const, gap: "1rem" },
  input: {
    padding: "0.75rem 1rem",
    borderRadius: "8px",
    border: "1px solid #ddd",
    fontSize: "1rem",
  },
  button: {
    padding: "0.75rem",
    backgroundColor: "#7C3AED",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "1rem",
    cursor: "pointer",
    fontWeight: 600,
  },
  error: { color: "#e53935", fontSize: "0.9rem", margin: 0 },
  switchText: { marginTop: "1rem", color: "#666" },
  switchLink: { color: "#7C3AED", cursor: "pointer", fontWeight: 600 },
};