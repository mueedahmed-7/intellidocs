import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Register() {

  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleRegister = (e) => {

    e.preventDefault();

    if (password !== confirmPassword) {

      alert("Passwords do not match");

      return;
    }

    console.log({
      name,
      email,
      password
    });

    /*
      Registration will be sent to backend later.

      After successful account creation,
      user MUST register their face.
    */

    navigate("/face-register");
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
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
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


          <button
            type="submit"
            className="auth-button"
          >
            Create Account
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