/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState } from "react";
import {
  apiFetch,
  AUTH_SESSION_CHANGED,
  clearSession,
  getStoredToken,
  getStoredUser,
  storeSession,
} from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser());
  const [isRestoring, setIsRestoring] = useState(() => Boolean(getStoredToken()));

  const restoreSession = async () => {
    if (!getStoredToken()) {
      setUser(null);
      setIsRestoring(false);
      return;
    }

    try {
      const response = await apiFetch("/auth/me", {}, { auth: true });
      if (!response.ok) {
        clearSession();
        setUser(null);
        return;
      }

      const restoredUser = await response.json();
      storeSession({ access_token: getStoredToken(), user: restoredUser });
      setUser(restoredUser);
    } catch {
      clearSession();
      setUser(null);
    } finally {
      setIsRestoring(false);
    }
  };

  useEffect(() => {
    let restoreTimer;
    if (getStoredToken()) {
      restoreTimer = window.setTimeout(() => {
        void restoreSession();
      }, 0);
    }
    const syncSession = () => setUser(getStoredUser());
    window.addEventListener(AUTH_SESSION_CHANGED, syncSession);
    return () => {
      if (restoreTimer) window.clearTimeout(restoreTimer);
      window.removeEventListener(AUTH_SESSION_CHANGED, syncSession);
    };
  }, []);

  const setSession = (session) => {
    storeSession(session);
    setUser(session.user);
  };

  const logout = () => {
    clearSession();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isRestoring, setSession, logout, restoreSession }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider.");
  return context;
}
