// Central place for the backend URL.
// The sole browser-side source of truth for the backend URL.
// A local Frontend/.env overrides this with VITE_API_BASE_URL.
export const API_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const TOKEN_KEY = "access_token";
const USER_KEY = "authenticated_user";
export const AUTH_SESSION_CHANGED = "auth-session-changed";

function notifySessionChange() {
  window.dispatchEvent(new Event(AUTH_SESSION_CHANGED));
}

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  try {
    const value = localStorage.getItem(USER_KEY);
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}

export function storeSession({ access_token, user }) {
  localStorage.setItem(TOKEN_KEY, access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  notifySessionChange();
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  // Clear the legacy keys used by the earlier face-login implementation.
  localStorage.removeItem("user_id");
  localStorage.removeItem("user_name");
  localStorage.removeItem("user_email");
  notifySessionChange();
}

export async function apiFetch(path, options = {}, { auth = false } = {}) {
  const headers = new Headers(options.headers || {});
  const token = getStoredToken();

  if (auth && token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        "Cannot connect to the local IntelliDocs server. Make sure the backend is running.",
        { cause: error },
      );
    }
    throw error;
  }

  if (auth && response.status === 401) {
    clearSession();
  }

  return response;
}
