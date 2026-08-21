import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import "./App.css";

import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import FaceRegister from "./pages/FaceRegister.jsx";
import FaceLogin from "./pages/FaceLogin.jsx";
import Chat from "./pages/Chat.jsx";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("access_token");

  return token ? children : <Navigate to="/login" replace />;
}

function App() {

  return (
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
          element={<FaceRegister />}
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
  );
}

export default App;
