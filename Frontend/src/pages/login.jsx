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
import { apiFetch } from "../api";
import { useAuth } from "../auth";


function Login() {

  const navigate = useNavigate();
  const { setSession } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {

    e.preventDefault();

    setError("");
    setLoading(true);

    try {

      const response = await apiFetch(
        "/auth/login",
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

      setSession(data);

      // Go to chatbot
      navigate("/chat");

    } catch (error) {

      console.error("Login error:", error);

      setError(error.message || "Login failed. Please try again.");

    } finally {

      setLoading(false);
    }
  };

  return (

    <div className="auth-page auth-split-page">
      <section className="auth-marketing" aria-label="IntelliDocs benefits">
        <div className="logo">Intelli<span>Docs</span></div>
        <p className="auth-tagline">Ask. Understand. Do More.</p>
        <div className="auth-marketing-copy">
          <h1>Your documents,<br />smarter answers.</h1>
          <p>Upload, ask, and get accurate answers powered by AI.</p>
          <ul><li>▣ <span>Chat with your documents</span></li><li>✦ <span>Get clear, sourced answers</span></li><li>◉ <span>Secure and private</span></li><li>▴ <span>Built for students and professionals</span></li></ul>
        </div>
        <div className="auth-illustration" aria-hidden="true"><span>✦</span><em>Knowledge<br />in your hands</em></div>
      </section>

      <div className="auth-card auth-form-card">

        <div className="logo">
          Intelli<span>Docs</span>
        </div>

        <h1>Welcome back</h1>

        <p className="subtitle">
          Sign in to your IntelliDocs account
        </p>

        <form onSubmit={handleLogin}>

          <div className="input-group">

            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

          </div>

          <div className="input-group">

            <input
              type="password"
              placeholder="Password"
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
            {loading ? "Signing in..." : "Sign In"}
          </button>

        </form>

        <div className="divider">
          <span>OR CONTINUE WITH</span>
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
