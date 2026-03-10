export default function UserHabits() {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>🏆 My Habits</h1>
        <p style={styles.subtitle}>Your habit tracking dashboard will live here.</p>
        <div style={styles.placeholder}>
          <p>📋 Habit list coming soon</p>
          <p>🔥 Streak tracking coming soon</p>
          <p>📅 Calendar heatmap coming soon</p>
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "#F5F3FF" },
  card: { backgroundColor: "#fff", padding: "2.5rem", borderRadius: "12px", boxShadow: "0 4px 20px rgba(0,0,0,0.1)", textAlign: "center" as const, width: "90%", maxWidth: "500px" },
  title: { fontSize: "1.8rem", marginBottom: "0.5rem" },
  subtitle: { color: "#666", marginBottom: "1.5rem" },
  placeholder: { backgroundColor: "#F5F3FF", borderRadius: "8px", padding: "1.5rem", color: "#7C3AED", lineHeight: "2" },
};