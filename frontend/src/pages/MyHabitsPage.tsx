import { useEffect, useState } from "react";

interface Habit {
  id: number;
  name: string;
  description: string;
  current_streak: number;
  longest_streak: number;
}

export default function MyHabitsPage() {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  
  // Modal State
  const [editingId, setEditingId] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");
  
  const [loggedToday, setLoggedToday] = useState<Record<number, boolean>>({});
  const token = localStorage.getItem("token");

  async function fetchHabits() {
    try {
      const res = await fetch("http://localhost:8000/habits", {
        headers: { "Authorization": `Bearer ${token}` },
      });
      const data = await res.json();
      if (Array.isArray(data)) {
        setHabits(data);
        const today = new Date().toISOString().split('T')[0];
        const logStatus: Record<number, boolean> = {};
        for (const habit of data) {
          const statsRes = await fetch(`http://localhost:8000/habits/${habit.id}/stats`, {
            headers: { "Authorization": `Bearer ${token}` },
          });
          const stats = await statsRes.json();
          if (stats.last_logged_date === today) logStatus[habit.id] = true;
        }
        setLoggedToday(logStatus);
      }
    } catch (err) { console.error(err); } finally { setLoading(false); }
  }

  useEffect(() => { fetchHabits(); }, []);

  // delete  
  async function handleDelete(habitId: number) {
    if (!window.confirm("Are you sure you want to delete this habit?")) return;
    try {
      const res = await fetch(`http://localhost:8000/habits/${habitId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) fetchHabits();
    } catch (err) { console.error("Delete error:", err); }
  }

  function openEditModal(habit: Habit) {
    setEditingId(habit.id);
    setName(habit.name);
    setDescription(habit.description);
    setShowModal(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const method = editingId ? "PUT" : "POST";
    const url = editingId 
      ? `http://localhost:8000/habits/${editingId}?name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}`
      : `http://localhost:8000/habits?name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}`;

    try {
      const res = await fetch(url, {
        method: method,
        headers: { "Authorization": `Bearer ${token}` },
      });

      if (res.ok) {
        setMessage(editingId ? "✅ Habit updated!" : "✅ Habit created!");
        setTimeout(() => {
          setShowModal(false);
          setEditingId(null);
          setName("");
          setDescription("");
          setMessage("");
          fetchHabits();
        }, 1000);
      }
    } catch (err) { setMessage("❌ Error saving habit."); }
  }

  async function handleLog(habitId: number) {
    const res = await fetch(`http://localhost:8000/habits/${habitId}/log`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (res.ok) {
      setLoggedToday(prev => ({ ...prev, [habitId]: true }));
      fetchHabits();
    }
  }

  return (
    <div style={{ padding: "20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
        <h2>My Habits</h2>
        <button onClick={() => { setEditingId(null); setName(""); setDescription(""); setShowModal(true); }} className="new-habit-btn">
          + New Habit
        </button>
      </div>

      {loading ? <p>Loading...</p> : (
        <div style={styles.grid}>
          {habits.map((habit) => (
            <div key={habit.id} className={`habit-card ${loggedToday[habit.id] ? 'habit-card-logged' : ''}`}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <h3 style={{ margin: 0 }}>{habit.name}</h3>
                <div style={{ display: 'flex', gap: '5px' }}>
                  <button onClick={() => openEditModal(habit)} style={styles.iconBtn}>✏️edit</button>
                  <button onClick={() => handleDelete(habit.id)} style={styles.iconBtn}>🗑️delete</button> 
                </div>
              </div>
              <p style={{ color: "#666", fontSize: "0.9rem", margin: "10px 0" }}>{habit.description}</p>
              
              <div style={{ marginBottom: "15px", fontSize: "0.9rem" }}>
                🔥 {habit.current_streak} days | 🏆 Best: {habit.longest_streak}
              </div>

              <button 
                className="log-habit-button"
                onClick={() => handleLog(habit.id)}
                disabled={loggedToday[habit.id]}
              >
                {loggedToday[habit.id] ? "✓ Logged" : "✓ Log Today"}
              </button>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div style={modalStyles.overlay}>
          <div style={modalStyles.content}>
            <h3>{editingId ? "Edit Habit" : "New Habit"}</h3>
            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "15px" }}>
              <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required style={styles.input} />
              <textarea placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} style={styles.input} />
              {message && <p>{message}</p>}
              <div style={{ display: "flex", gap: "10px" }}>
                <button type="submit" className="new-habit-btn" style={{ flex: 1 }}>{editingId ? "Update" : "Save"}</button>
                <button type="button" onClick={() => setShowModal(false)} style={{ flex: 1, padding: "10px", borderRadius: "5px", border: "1px solid #ccc", background: "none" }}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "20px" },
  iconBtn: { background: "none", border: "none", cursor: "pointer", fontSize: "1.1rem", padding: "2px" },
  input: { padding: "10px", borderRadius: "5px", border: "1px solid #ddd" }
};

const modalStyles: Record<string, React.CSSProperties> = {
  overlay: { position: "fixed", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 },
  content: { backgroundColor: "white", padding: "30px", borderRadius: "12px", width: "90%", maxWidth: "400px" }
};