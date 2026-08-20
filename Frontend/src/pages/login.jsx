import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

function Login() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {

    e.preventDefault();

    console.log("Email:", email);
    console.log("Password:", password);

    // Backend authentication will be connected later

    navigate("/chat");
  };

  const handleFaceLogin = () => {

    // Face login will be connected later

    console.log("Face Login clicked");

  };

  return (

    <div className="auth-page">

      <div className="auth-card">

        <div className="logo">
          RAG<span>CHAT</span>
        </div>

        <h1>Welcome Back</h1>

        <p className="subtitle">
          Login to your AI document assistant
        </p>

        <form onSubmit={handleLogin}>

          <div className="input-group">

            <label>Email</label>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

          </div>

          <div className="input-group">

            <label>Password</label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

          </div>

          <button
            type="submit"
            className="auth-button"
          >
            Login
          </button>

        </form>

        <div className="divider">
          <span>OR</span>
        </div>

        <button
          type="button"
          className="face-login-button"
          onClick={() => navigate("/face-login")}
        >
          📷 Login with Face
        </button>

        <p className="switch-page">

          Don't have an account?

          {" "}

          <Link to="/register">
            Create account
          </Link>

        </p>

      </div>

    </div>

  );
}

export default Login;