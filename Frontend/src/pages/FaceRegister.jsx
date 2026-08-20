// import { useRef, useState } from "react";
// import { useNavigate } from "react-router-dom";

// function FaceRegister() {
//   const videoRef = useRef(null);
//   const streamRef = useRef(null);

//   const [cameraStarted, setCameraStarted] = useState(false);
//   const [error, setError] = useState("");
//   const [message, setMessage] = useState("");
//   const [registering, setRegistering] = useState(false);

//   const navigate = useNavigate();

//   // ============================================================
//   // START CAMERA
//   // ============================================================

//   const startCamera = async () => {

//     try {

//       setError("");

//       const response = await fetch(
//         "http://127.0.0.1:8000/face/register",
//         {
//           method: "POST",
//         }
//       );

//       const data = await response.json();

//       console.log(data);

//       if (!data.success) {
//         setError(data.message);
//       }

//     } catch (err) {

//       console.error(err);

//       setError(
//         "Could not connect to face registration backend."
//       );

//     }
//   };

//   // ============================================================
//   // STOP CAMERA
//   // ============================================================

//   const stopCamera = () => {
//     if (streamRef.current) {
//       streamRef.current.getTracks().forEach((track) => {
//         track.stop();
//       });

//       streamRef.current = null;
//     }
//   };

//   // ============================================================
//   // CAPTURE FACE
//   // ============================================================

//   const registerFace = async () => {
//     if (!videoRef.current) {
//       setError("Camera is not available.");
//       return;
//     }

//     try {
//       setRegistering(true);
//       setError("");
//       setMessage("Capturing your face...");




//       // --------------------------------------------------------
//       // Create canvas
//       // --------------------------------------------------------

//       const video = videoRef.current;

//       const canvas = document.createElement("canvas");

//       canvas.width = video.videoWidth;
//       canvas.height = video.videoHeight;

//       const context = canvas.getContext("2d");

//       context.drawImage(
//         video,
//         0,
//         0,
//         canvas.width,
//         canvas.height
//       );

//       // --------------------------------------------------------
//       // Convert captured frame to JPEG
//       // --------------------------------------------------------

//       const blob = await new Promise((resolve) => {
//         canvas.toBlob(
//           resolve,
//           "image/jpeg",
//           0.9
//         );
//       });

//       if (!blob) {
//         throw new Error("Could not capture image.");
//       }

//       // --------------------------------------------------------
//       // Username
//       // --------------------------------------------------------
//       //
//       // TEMPORARY:
//       // We will later get this from the logged-in/registered
//       // user's account.
//       //
//       // For now browser asks for username.
//       // --------------------------------------------------------

//       const username = window.prompt(
//         "Enter your username:"
//       );

//       if (!username) {
//         setRegistering(false);
//         setMessage("");
//         return;
//       }

//       // --------------------------------------------------------
//       // Create multipart form
//       // --------------------------------------------------------

//       const formData = new FormData();

//       formData.append(
//         "username",
//         username
//       );

//       formData.append(
//         "image",
//         blob,
//         "face.jpg"
//       );

//       // --------------------------------------------------------
//       // Send image to FastAPI
//       // --------------------------------------------------------

//       setMessage(
//         "Sending face to server..."
//       );

//       const response = await fetch(
//         "http://127.0.0.1:8000/face/register",
//         {
//           method: "POST",
//           body: formData,
//         }
//       );

//       // --------------------------------------------------------
//       // Read backend response
//       // --------------------------------------------------------

//       const result = await response.json();

//       console.log(
//         "Backend response:",
//         result
//       );

//       // --------------------------------------------------------
//       // Handle response
//       // --------------------------------------------------------

//       if (!result.success) {
//         setError(
//           result.message ||
//           "Face registration failed."
//         );

//         setMessage("");
//         setRegistering(false);

//         return;
//       }

//       // --------------------------------------------------------
//       // SUCCESS
//       // --------------------------------------------------------

//       setMessage(
//         "Face registered successfully!"
//       );

//       stopCamera();

//       setCameraStarted(false);

//       setTimeout(() => {
//         navigate("/login");
//       }, 1500);

//     } catch (err) {
//       console.error(err);

//       setError(
//         "Could not connect to the face registration server."
//       );

//       setMessage("");
//     } finally {
//       setRegistering(false);
//     }
//   };

//   // ============================================================
//   // UI
//   // ============================================================

//   return (
//     <div className="auth-page">

//       <div className="auth-card face-card">

//         <div className="logo">
//           RAG<span>CHAT</span>
//         </div>

//         <h1>
//           Register Your Face
//         </h1>

//         <p className="subtitle">
//           Face registration is required to complete your account.
//         </p>

//         <div className="camera-container">

//           {!cameraStarted && (
//             <div className="camera-placeholder">
//               📷
//             </div>
//           )}

//           <video
//             ref={videoRef}
//             autoPlay
//             playsInline
//             className="camera-video"
//           />

//         </div>

//         {error && (
//           <p className="camera-error">
//             {error}
//           </p>
//         )}

//         {message && (
//           <p>
//             {message}
//           </p>
//         )}

//         {!cameraStarted ? (

//           <button
//             type="button"
//             className="auth-button"
//             onClick={startCamera}
//           >
//             Start Camera
//           </button>

//         ) : (

//           <button
//             type="button"
//             className="auth-button"
//             onClick={registerFace}
//             disabled={registering}
//           >
//             {registering
//               ? "Registering..."
//               : "Register Face"}
//           </button>

//         )}

//         <p className="required-message">
//           Face registration is required before you can continue.
//         </p>

//       </div>

//     </div>
//   );
// }

// export default FaceRegister;

import { useState } from "react";
import { useNavigate } from "react-router-dom";

function FaceRegister() {
  const [registering, setRegistering] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  // ============================================================
  // START PYTHON FACE REGISTRATION
  // ============================================================

  const startRegistration = async () => {
    try {
      setError("");
      setMessage("");
      setRegistering(true);

      // Ask for username
      const username = window.prompt(
        "Enter your username:"
      );

      if (!username || !username.trim()) {
        setError("Username is required.");
        setRegistering(false);
        return;
      }

      setMessage(
        "Starting Python face registration camera..."
      );

      // --------------------------------------------------------
      // Send username to FastAPI
      // --------------------------------------------------------

      const formData = new FormData();

      formData.append(
        "username",
        username.trim()
      );

      const response = await fetch(
        "http://127.0.0.1:8000/face/register",
        {
          method: "POST",
          body: formData,
        }
      );

      // --------------------------------------------------------
      // Check HTTP response
      // --------------------------------------------------------

      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}`
        );
      }

      const result = await response.json();

      console.log(
        "Face registration response:",
        result
      );

      // --------------------------------------------------------
      // Registration failed
      // --------------------------------------------------------

      if (!result.success) {
        setError(
          result.message ||
          "Face registration failed."
        );

        setMessage("");
        setRegistering(false);

        return;
      }

      // --------------------------------------------------------
      // Registration successful
      // --------------------------------------------------------

      setMessage(
        "Face registration completed successfully!"
      );

      setRegistering(false);

      // Go to login after successful registration
      setTimeout(() => {
        navigate("/login");
      }, 1500);

    } catch (err) {
      console.error(
        "Face registration error:",
        err
      );

      setError(
        "Could not connect to the face registration server. Make sure FastAPI is running."
      );

      setMessage("");
      setRegistering(false);
    }
  };

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="auth-page">

      <div className="auth-card face-card">

        <div className="logo">
          RAG<span>CHAT</span>
        </div>

        <h1>
          Register Your Face
        </h1>

        <p className="subtitle">
          Face registration is required to complete your account.
        </p>

        {/* =====================================================
            CAMERA PLACEHOLDER
        ===================================================== */}

        <div className="camera-container">

          <div className="camera-placeholder">
            📷
          </div>

        </div>

        {/* =====================================================
            ERROR
        ===================================================== */}

        {error && (
          <p className="camera-error">
            {error}
          </p>
        )}

        {/* =====================================================
            STATUS MESSAGE
        ===================================================== */}

        {message && (
          <p>
            {message}
          </p>
        )}

        {/* =====================================================
            REGISTER BUTTON
        ===================================================== */}

        <button
          type="button"
          className="auth-button"
          onClick={startRegistration}
          disabled={registering}
        >
          {registering
            ? "Registration Running..."
            : "Open Camera & Register Face"}
        </button>

        {/* =====================================================
            INSTRUCTIONS
        ===================================================== */}

        <p className="required-message">
          Clicking the button will open the Python
          face-registration camera.
        </p>

        <p className="required-message">
          You will register your face from:
          <br />
          <strong>FRONT → LEFT → RIGHT</strong>
        </p>

      </div>

    </div>
  );
}

export default FaceRegister;