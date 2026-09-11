import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import "./App.css";

import Login from "./pages/login.jsx";
import Register from "./pages/register.jsx";
import FaceRegister from "./pages/FaceRegister.jsx";
import FaceLogin from "./pages/facelogin.jsx";
import Chat from "./pages/chat.jsx";
import { AuthProvider, useAuth } from "./auth";

function ProtectedRoute({ children }) {
  const { user, isRestoring } = useAuth();

  if (isRestoring) return null;
  return user ? children : <Navigate to="/login" replace />;
}

function App() {

  return (
    <AuthProvider>
    <BrowserRouter>

      <Routes>

        {/* Home */}

        <Route
          path="/"
          element={<Navigate to="/login" replace />}
        />


        {/* Login */}

        <Route
          path="/login"
          element={<Login />}
        />


        {/* Registration */}

        <Route
          path="/register"
          element={<Register />}
        />


        {/* Mandatory Face Registration */}

        <Route
          path="/face-register"
          element={<ProtectedRoute><FaceRegister /></ProtectedRoute>}
        />


        {/* Face Login */}

        <Route
          path="/face-login"
          element={<FaceLogin />}
        />


        {/* Chat */}

        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />


        {/* Unknown URL */}

        <Route
          path="*"
          element={<Navigate to="/login" replace />}
        />

      </Routes>

    </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
