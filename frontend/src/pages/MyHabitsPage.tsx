import { useEffect, useState } from "react";
import GlobalHabitHeatmap from "../components/GlobalHabitHeatmap";

interface Habit {
  id: number;
  name: string;
  description: string;
  current_streak: number;
  longest_streak: number;
}

interface MyHabitsPageProps {
  externalOpenModal?: boolean;
  onModalClose?: () => void;
}

export default function MyHabitsPage({ externalOpenModal, onModalClose }: MyHabitsPageProps) {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [heatmapKey, setHeatmapKey] = useState(0);

  // Modal State
  const [editingId, setEditingId] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");

  const [loggedToday, setLoggedToday] = useState<Record<number, boolean>>({});
  const token = localStorage.getItem("token");

  // New Habit button
  useEffect(() => {
    if (externalOpenModal) {
      setEditingId(null);
      setName("");
      setDescription("");
      setShowModal(true);
    }
  }, [externalOpenModal]);

  async function fetchHabits() {
    try {
      const res = await fetch("/api/habits", {
        headers: { "Authorization": `Bearer ${token}` },
      });
      const data = await res.json();

      if (Array.isArray(data)) {
        setHabits(data);
        const today = new Date();
        const localToday = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
        const logStatus: Record<number, boolean> = {};

        for (const habit of data) {
          const statsRes = await fetch(`/api/habits/${habit.id}/stats`, {
            headers: { "Authorization": `Bearer ${token}` },
          });
          if (statsRes.ok) {
            const stats = await statsRes.json();
            if (stats.last_logged_date === localToday) {
              logStatus[habit.id] = true;
            }
          }
        }
        setLoggedToday(logStatus);
      }
    } catch (err) {
      console.error("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchHabits();
  }, []);

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
    setName("");
    setDescription("");
    setMessage("");
    onModalClose?.();
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;

    const method = editingId ? "PUT" : "POST";
    const url = editingId 
      ? `/api/habits/${editingId}?name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}`
      : `/api/habits?name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}`;

    try {
      const res = await fetch(url, {
        method,
        headers: { "Authorization": `Bearer ${token}` },
      });

      if (res.ok) {
        setMessage(editingId ? "✅ Habit updated!" : "✅ Habit created!");
        setTimeout(() => {
          handleCloseModal();
          fetchHabits();
        }, 500);
      } else {
        setMessage("❌ Error saving habit.");
      }
    } catch (err) {
      console.error("Network error:", err);
      setMessage("❌ Network error");
    }
  }

  async function handleLog(habitId: number) {
    try {
      // Get local date as YYYY-MM-DD, not UTC
      const today = new Date();
      const localDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

      const res = await fetch(`/api/habits/${habitId}/log?log_date=${localDate}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        setLoggedToday(prev => ({ ...prev, [habitId]: true }));
        fetchHabits();
        setHeatmapKey(prev => prev + 1);
      }
    } catch (err) {
      console.error("Log error:", err);
    }
  }

  async function handleDelete(habitId: number) {
    if (!window.confirm("Are you sure you want to delete this habit?")) return;
    try {
      const res = await fetch(`/api/habits/${habitId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) fetchHabits();
    } catch (err) {
      console.error("Delete error:", err);
    }
  }

  function openEditModal(habit: Habit) {
    setEditingId(habit.id);
    setName(habit.name);
    setDescription(habit.description);
    setShowModal(true);
  }

  return (
    <>

      <div style={{ padding: "20px" }}>
        <div style={{ marginBottom: "10px" }}>
          <GlobalHabitHeatmap refreshKey={heatmapKey} />
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
          <h2>My Habits</h2>
          <button
            onClick={() => { setEditingId(null); setName(""); setDescription(""); setShowModal(true); }}
            className="new-habit-btn"
          >
            + New Habit
          </button>
        </div>

        {loading ? (
          <p>Loading habits...</p>
        ) : habits.length === 0 ? (
          <div className="empty-state-card">
            <p>No habits yet - create your first!</p>
          </div>
        ) : (
          <div style={styles.grid}>
            {habits.map((habit) => (
              <div key={habit.id} className={`habit-card ${loggedToday[habit.id] ? 'habit-card-logged' : ''}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <h3 style={{ margin: 0 }}>{habit.name}</h3>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button onClick={() => openEditModal(habit)} style={styles.iconBtn} title="Edit">✏️</button>
                    <button onClick={() => handleDelete(habit.id)} style={styles.iconBtn} title="Delete">🗑️</button>
                  </div>
                </div>

                <p style={{ color: "#666", fontSize: "0.9rem", margin: "10px 0" }}>
                  {habit.description || "No description provided."}
                </p>

                <div style={{ marginBottom: "15px", fontSize: "0.9rem", fontWeight: "600" }}>
                  <span style={{ color: "#f97316" }}>🔥 {habit.current_streak} days</span>
                  <span style={{ color: "#888", marginLeft: "10px" }}>🏆 Best: {habit.longest_streak}</span>
                </div>

                <button
                  className="log-habit-button"
                  onClick={() => handleLog(habit.id)}
                  disabled={loggedToday[habit.id]}
                >
                  {loggedToday[habit.id] ? "✓ Logged Today" : "✓ Log Today"}
                </button>
              </div>
            ))}
          </div>
        )}

        {showModal && (
          <div style={modalStyles.overlay}>
            <div style={modalStyles.content}>
              <h3 style={{ marginBottom: "15px" }}>{editingId ? "Edit Habit" : "New Habit"}</h3>
              <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                <input
                  type="text"
                  placeholder="Name (Required)"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  style={styles.input}
                />
                <textarea
                  placeholder="Description (Optional)"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  style={{ ...styles.input, minHeight: "80px" }}
                />
                {message && <p style={{ color: "#7C3AED", fontWeight: "bold", textAlign: "center", margin: 0 }}>{message}</p>}
                <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
                  <button type="submit" className="new-habit-btn" style={{ flex: 1 }}>
                    {editingId ? "Update" : "Save"}
                  </button>
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    style={{ flex: 1, padding: "10px", borderRadius: "8px", border: "1px solid #ccc", background: "none", cursor: "pointer" }}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

const styles = {
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: "20px"
  },
  iconBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    fontSize: "1rem",
    padding: "4px",
    borderRadius: "4px",
    transition: "background 0.2s"
  },
  input: {
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid #ddd",
    fontSize: "1rem"
  }
};

const modalStyles: Record<string, React.CSSProperties> = {
  overlay: {
    position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: "rgba(0,0,0,0.5)", display: "flex",
    alignItems: "center", justifyContent: "center", zIndex: 1000
  },
  content: {
    backgroundColor: "white", padding: "30px", borderRadius: "12px",
    width: "90%", maxWidth: "400px", boxShadow: "0 10px 25px rgba(0,0,0,0.2)"
  }
};