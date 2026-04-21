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

export interface UserProfile {
  id: number;
  username: string;
}

export interface EventAttendee {
  id?: number;
  event_id?: number;
  user_id: number;
  status: "invited" | "accepted" | "declined";
  invited_at?: string;
  responded_at?: string | null;
  user?: {
    id: number;
    username: string;
  };
}

export interface Event {
  id: number;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  location: string;
  creator_id: number;
  attendees: EventAttendee[];
}

export interface CreateEventData {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  invite_user_ids?: number[];
}

export interface UpdateEventData {
  title?: string;
  description?: string;
  start_time?: string;
  end_time?: string;
  location?: string;
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

// ----------------------------------------------------------------------------------
// Event API integration

export async function getProfile(): Promise<UserProfile> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/auth/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch profile");
  return data;
}

export async function getEvents(startDate?: string, endDate?: string): Promise<Event[]> {
  const token = localStorage.getItem("token");
  const params = new URLSearchParams();
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);

  const query = params.toString();
  const url = `${BASE_URL}/events${query ? `?${query}` : ""}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch events");
  return data;
}

export async function createEvent(data: CreateEventData): Promise<Event> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/events`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  const payload = await res.json();
  if (!res.ok) throw new Error(payload.detail || "Failed to create event");
  return payload;
}

export async function updateEvent(id: number, data: UpdateEventData): Promise<Event> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/events/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  const payload = await res.json();
  if (!res.ok) throw new Error(payload.detail || "Failed to update event");
  return payload;
}

export async function deleteEvent(id: number): Promise<void> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/events/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const payload = await res.json();
    throw new Error(payload.detail || "Failed to delete event");
  }
}

export async function inviteUsers(eventId: number, userIds: number[]): Promise<void> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/events/${eventId}/invite`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ user_ids: userIds }),
  });

  if (!res.ok) {
    const payload = await res.json();
    throw new Error(payload.detail || "Failed to invite users");
  }
}

export async function respondToInvite(eventId: number, statusValue: "accepted" | "declined"): Promise<void> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}/events/${eventId}/respond`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ status: statusValue }),
  });

  if (!res.ok) {
    const payload = await res.json();
    throw new Error(payload.detail || "Failed to respond to invite");
  }
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