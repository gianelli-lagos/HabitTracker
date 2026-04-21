export interface Notification {
  id: number;
  user_id: number;
  type: string;
  title: string;
  message: string;
  data: any;
  is_read: boolean;
  created_at: string;
  read_at: string | null;
}

export interface Habit {
  id: number;
  name: string;
  description: string;
  current_streak: number;
  longest_streak: number;
  is_active: boolean;
  created_at: string;
}

export interface HabitLog {
  id: number;
  habit_id: number;
  date: string;
  logged_at: string;
}



const BASE_URL = "http://localhost:8000";

export async function registerUser(username: string, password: string) {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to Register");
  return data;
}
export async function loginUser(username: string, password: string) {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Login failed");

  localStorage.setItem("token", data.access_token);
  return data;
}

export function logoutUser() {
  localStorage.removeItem("token");
}

export function isLoggedIn(): boolean {
  const token = localStorage.getItem("token");
  if (token) {
    return true;
  } else {
    return false;
  }
}

// Notification System types and functions
export async function getNotifications(unreadOnly = false): Promise<Notification[]> {
  const token = localStorage.getItem("token");
  const url = `${BASE_URL}/notifications${unreadOnly ? "?unread_only=true" : ""}`;
  
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });
  
  if (!res.ok) throw new Error("Failed to fetch notifications");
  return res.json();
}

export async function getUnreadCount(): Promise<number> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/notifications/unread-count`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  
  if (!res.ok) throw new Error("Failed to fetch unread count");
  const data = await res.json();
  return data.count;
}

export async function markAsRead(notificationId: number): Promise<void> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/notifications/${notificationId}/read`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}` }
  });
  
  if (!res.ok) throw new Error("Failed to mark as read");
}

export async function markAllAsRead(): Promise<void> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/notifications/read-all`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}` }
  });
  
  if (!res.ok) throw new Error("Failed to mark all as read");
}

export async function deleteNotification(notificationId: number): Promise<void> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/notifications/${notificationId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });
  
  if (!res.ok) throw new Error("Failed to delete notification");
}

// ---------------------------------------------------------------------------------- 
// ---------------------------------------------------------------------------------- 
// habit API integration

export async function createHabit(name: string, description?: string): Promise<Habit> {
  const token = localStorage.getItem("token");

  const res = await fetch(`${BASE_URL}/habits`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ name, description })
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to create habit");
  return data;
}


export async function getHabits(): Promise<Habit[]> {
  const token = localStorage.getItem("token");

  const res = await fetch(`${BASE_URL}/habits`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) throw new Error("Failed to fetch habits");
  return res.json();
}


export async function updateHabit(id: number, name: string, description?: string): Promise<Habit> {
  const token = localStorage.getItem("token");

  const res = await fetch(`${BASE_URL}/habits/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ name, description })
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to update habit");
  return data;
}

export async function deleteHabit(id: number): Promise<void> {
  const token = localStorage.getItem("token");

  const res = await fetch(`${BASE_URL}/habits/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) throw new Error("Failed to delete habit");
}

export async function logHabit(id: number): Promise<{ success: boolean, current_streak: number }> {
  const token = localStorage.getItem("token");

  const res = await fetch(`${BASE_URL}/habits/${id}/log`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to log habit");
  return data;
}

export async function getHabitLogs(id: number): Promise<HabitLog[]> {
  const token = localStorage.getItem("token");

  const res = await fetch(`${BASE_URL}/habits/${id}/logs`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) throw new Error("Failed to fetch habit logs");
  return res.json();
}

// Heatmap --
export async function getAllHabitsHeatmap() {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/habits/logs/all`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Failed to fetch global heatmap");
  return res.json();
}

// Profile Picture Upload
export async function uploadProfilePicture(file: File): Promise<{ profile_picture_url: string }> {
  const token = localStorage.getItem("token");
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/users/upload-profile-picture`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to upload picture");
  return data;
}