// // import { useState } from "react";
// // import { Link, useNavigate } from "react-router-dom";

// // function Register() {

// //   const navigate = useNavigate();

// //   const [name, setName] = useState("");
// //   const [email, setEmail] = useState("");
// //   const [password, setPassword] = useState("");
// //   const [confirmPassword, setConfirmPassword] = useState("");

// //   const handleRegister = (e) => {

// //     e.preventDefault();

// //     if (password !== confirmPassword) {

// //       alert("Passwords do not match");

// //       return;
// //     }

// //     console.log({
// //       name,
// //       email,
// //       password
// //     });

// //     /*
// //       Registration will be sent to backend later.

// //       After successful account creation,
// //       user MUST register their face.
// //     */

// //     navigate("/face-register");
// //   };


// //   return (

// //     <div className="auth-page">

// //       <div className="auth-card">

// //         <div className="logo">
// //           RAG<span>CHAT</span>
// //         </div>

// //         <h1>Create Account</h1>

// //         <p className="subtitle">
// //           Create your RAG chatbot account
// //         </p>


// //         <form onSubmit={handleRegister}>

// //           <div className="input-group">

// //             <label>Full Name</label>

// //             <input
// //               type="text"
// //               placeholder="Enter your name"
// //               value={name}
// //               onChange={(e) => setName(e.target.value)}
// //               required
// //             />

// //           </div>


// //           <div className="input-group">

// //             <label>Email</label>

// //             <input
// //               type="email"
// //               placeholder="Enter your email"
// //               value={email}
// //               onChange={(e) => setEmail(e.target.value)}
// //               required
// //             />

// //           </div>


// //           <div className="input-group">

// //             <label>Password</label>

// //             <input
// //               type="password"
// //               placeholder="Create a password"
// //               value={password}
// //               onChange={(e) => setPassword(e.target.value)}
// //               required
// //             />

// //           </div>


// //           <div className="input-group">

// //             <label>Confirm Password</label>

// //             <input
// //               type="password"
// //               placeholder="Confirm your password"
// //               value={confirmPassword}
// //               onChange={(e) =>
// //                 setConfirmPassword(e.target.value)
// //               }
// //               required
// //             />

// //           </div>


// //           <button
// //             type="submit"
// //             className="auth-button"
// //           >
// //             Create Account
// //           </button>

// //         </form>


// //         <p className="switch-page">

// //           Already have an account?

// //           {" "}

// //           <Link to="/login">
// //             Login
// //           </Link>

// //         </p>

// //       </div>

// //     </div>

// //   );
// // }

// // export default Register;

// import { useState } from "react";
// import { Link, useNavigate } from "react-router-dom";
// import { API_URL } from "../api";

// function Register() {

//   const navigate = useNavigate();

//   const [name, setName] = useState("");
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [confirmPassword, setConfirmPassword] = useState("");
//   const [error, setError] = useState("");
//   const [submitting, setSubmitting] = useState(false);

//   const handleRegister = async (e) => {

//     e.preventDefault();
//     setError("");

//     if (password !== confirmPassword) {
//       setError("Passwords do not match");
//       return;
//     }

//     setSubmitting(true);

//     try {
//       // 1. Create the account
//       const registerResponse = await fetch(`${API_URL}/auth/register`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ name, email, password }),
//       });

//       const registerData = await registerResponse.json();

//       if (!registerResponse.ok) {
//         setError(registerData.detail || "Registration failed.");
//         setSubmitting(false);
//         return;
//       }

//       // 2. Log the new account in right away, so the face-registration
//       //    step (which requires a Bearer token) can use it immediately.
//       const loginResponse = await fetch(`${API_URL}/auth/login`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ email, password }),
//       });

//       const loginData = await loginResponse.json();

//       if (!registerResponse.ok) {
//         if (Array.isArray(registerData.detail)) {
//           const messages = registerData.detail
//             .map((d) => `${d.loc[d.loc.length - 1]}: ${d.msg}`)
//             .join(" | ");
//           setError(messages);
//         } else {
//           setError(registerData.detail || "Registration failed.");
//         }
//         setSubmitting(false);
//         return;
//       }

//       localStorage.setItem("access_token", loginData.access_token);

//       // 3. Face registration is a required part of account setup.
//       navigate("/face-register");

//     } catch (err) {
//       console.error(err);
//       setError("Could not reach the backend. Is the server running?");
//       setSubmitting(false);
//     }
//   };


//   return (

//     <div className="auth-page">

//       <div className="auth-card">

//         <div className="logo">
//           RAG<span>CHAT</span>
//         </div>

//         <h1>Create Account</h1>

//         <p className="subtitle">
//           Create your RAG chatbot account
//         </p>


//         <form onSubmit={handleRegister}>

//           <div className="input-group">

//             <label>Full Name</label>

//             <input
//               type="text"
//               placeholder="Enter your name"
//               value={name}
//               onChange={(e) => setName(e.target.value)}
//               required
//             />

//           </div>


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
//               placeholder="Create a password"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               required
//             />

//           </div>


//           <div className="input-group">

//             <label>Confirm Password</label>

//             <input
//               type="password"
//               placeholder="Confirm your password"
//               value={confirmPassword}
//               onChange={(e) =>
//                 setConfirmPassword(e.target.value)
//               }
//               required
//             />

//           </div>

//           {error && (
//             <p className="camera-error">{error}</p>
//           )}

//           <button
//             type="submit"
//             className="auth-button"
//             disabled={submitting}
//           >
//             {submitting ? "Creating Account..." : "Create Account"}
//           </button>

//         </form>


//         <p className="switch-page">

//           Already have an account?

//           {" "}

//           <Link to="/login">
//             Login
//           </Link>

//         </p>

//       </div>

//     </div>

//   );
// }

// export default Register;
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { API_URL } from "../api";

function Register() {

  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleRegister = async (e) => {

    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (new TextEncoder().encode(password).length > 72) {
      setError("Password must be 72 bytes or fewer.");
      return;
    }

    setSubmitting(true);

    try {
      // 1. Create the account
      const registerResponse = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      const registerData = await registerResponse.json();

      if (!registerResponse.ok) {
        // FastAPI validation errors (422) come back as detail: [{msg, loc, ...}]
        // instead of detail: "some string" like our other errors.
        if (Array.isArray(registerData.detail)) {
          const messages = registerData.detail
            .map((d) => `${d.loc[d.loc.length - 1]}: ${d.msg}`)
            .join(" | ");
          setError(messages);
        } else {
          setError(registerData.detail || "Registration failed.");
        }
        setSubmitting(false);
        return;
      }

      // 2. Log the new account in right away, so the face-registration
      //    step (which requires a Bearer token) can use it immediately.
      const loginResponse = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const loginData = await loginResponse.json();

      if (!loginResponse.ok) {
        setError("Account created, but automatic login failed. Please log in manually.");
        setSubmitting(false);
        navigate("/login");
        return;
      }

      localStorage.setItem("access_token", loginData.access_token);

      // 3. Face registration is a required part of account setup.
      navigate("/face-register");

    } catch (err) {
      console.error(err);
      setError("Could not reach the backend. Is the server running?");
      setSubmitting(false);
    }
  };


  return (

    <div className="auth-page">

      <div className="auth-card">

        <div className="logo">
          RAG<span>CHAT</span>
        </div>

        <h1>Create Account</h1>

        <p className="subtitle">
          Create your RAG chatbot account
        </p>


        <form onSubmit={handleRegister}>

          <div className="input-group">

            <label>Full Name</label>

            <input
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />

          </div>


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
              placeholder="Create a password (min 8 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              maxLength={72}
              required
            />

          </div>


          <div className="input-group">

            <label>Confirm Password</label>

            <input
              type="password"
              placeholder="Confirm your password"
              value={confirmPassword}
              onChange={(e) =>
                setConfirmPassword(e.target.value)
              }
              required
            />

          </div>

          {error && (
            <p className="camera-error">{error}</p>
          )}

          <button
            type="submit"
            className="auth-button"
            disabled={submitting}
          >
            {submitting ? "Creating Account..." : "Create Account"}
          </button>

        </form>


        <p className="switch-page">

          Already have an account?

          {" "}

          <Link to="/login">
            Login
          </Link>

        </p>

      </div>

    </div>

  );
}

export default Register;
