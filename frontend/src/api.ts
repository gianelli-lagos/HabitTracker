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