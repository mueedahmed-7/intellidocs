// import { Link, useNavigate } from "react-router-dom";
// import { useState } from "react";

// function Login() {

//   const navigate = useNavigate();

//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");

//   const handleLogin = (e) => {

//     e.preventDefault();

//     console.log("Email:", email);
//     console.log("Password:", password);

//     // Backend authentication will be connected later

//     navigate("/chat");
//   };

//   const handleFaceLogin = () => {

//     // Face login will be connected later

//     console.log("Face Login clicked");

//   };

//   return (

//     <div className="auth-page">

//       <div className="auth-card">

//         <div className="logo">
//           RAG<span>CHAT</span>
//         </div>

//         <h1>Welcome Back</h1>

//         <p className="subtitle">
//           Login to your AI document assistant
//         </p>

//         <form onSubmit={handleLogin}>

//           <div className="input-group">

//             <label>Email</label>

//             <input
//               type="email"
//               placeholder="Enter your email"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//               required
//             />

//           </div>

//           <div className="input-group">

//             <label>Password</label>

//             <input
//               type="password"
//               placeholder="Enter your password"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               required
//             />

//           </div>

//           <button
//             type="submit"
//             className="auth-button"
//           >
//             Login
//           </button>

//         </form>

//         <div className="divider">
//           <span>OR</span>
//         </div>

//         <button
//           type="button"
//           className="face-login-button"
//           onClick={() => navigate("/face-login")}
//         >
//           📷 Login with Face
//         </button>

//         <p className="switch-page">

//           Don't have an account?

//           {" "}

//           <Link to="/register">
//             Create account
//           </Link>

//         </p>

//       </div>

//     </div>

//   );
// }

// export default Login;
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

function Login() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {

    e.preventDefault();

    setError("");
    setLoading(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/auth/login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            email: email,
            password: password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {

        setError(
          data.detail || "Invalid email or password."
        );

        return;
      }

      // Save JWT token
      localStorage.setItem(
        "access_token",
        data.access_token
      );

      // Go to chatbot
      navigate("/chat");

    } catch (error) {

      console.error("Login error:", error);

      setError(
        "Could not connect to the server. Make sure FastAPI is running."
      );

    } finally {

      setLoading(false);
    }
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

          {error && (
            <p className="error-message">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="auth-button"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
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