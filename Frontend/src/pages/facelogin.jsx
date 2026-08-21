// // // import { useRef, useState } from "react";
// // // import { useNavigate, Link } from "react-router-dom";

// // // function FaceLogin() {

// // //   const videoRef = useRef(null);
// // //   const navigate = useNavigate();

// // //   const [cameraStarted, setCameraStarted] = useState(false);
// // //   const [error, setError] = useState("");

// // //   const startCamera = async () => {

// // //     try {

// // //       setError("");

// // //       const stream = await navigator.mediaDevices.getUserMedia({
// // //         video: true
// // //       });

// // //       videoRef.current.srcObject = stream;

// // //       setCameraStarted(true);

// // //     } catch (err) {

// // //       console.error(err);

// // //       setError(
// // //         "Camera permission is required for face login."
// // //       );

// // //     }
// // //   };


// // //   const verifyFace = () => {

// // //     /*
// // //       Face recognition will be connected here later.

// // //       Later:

// // //       1. Capture the user's face
// // //       2. Send it to the backend
// // //       3. Backend compares the face with MongoDB data
// // //       4. Backend returns authentication result
// // //       5. If successful, navigate to /chat
// // //     */

// // //     console.log("Face verification requested");

// // //     // Temporary navigation for frontend testing
// // //     navigate("/chat");
// // //   };


// // //   return (

// // //     <div className="auth-page">

// // //       <div className="auth-card face-card">

// // //         <div className="logo">
// // //           RAG<span>CHAT</span>
// // //         </div>


// // //         <h1>Face Login</h1>


// // //         <p className="subtitle">
// // //           Look directly at the camera to login
// // //         </p>


// // //         <div className="camera-container">

// // //           {!cameraStarted && (

// // //             <div className="camera-placeholder">
// // //               📷
// // //             </div>

// // //           )}


// // //           <video
// // //             ref={videoRef}
// // //             autoPlay
// // //             playsInline
// // //             className="camera-video"
// // //           />

// // //         </div>


// // //         {error && (

// // //           <p className="camera-error">
// // //             {error}
// // //           </p>

// // //         )}


// // //         {!cameraStarted ? (

// // //           <button
// // //             type="button"
// // //             className="auth-button"
// // //             onClick={startCamera}
// // //           >
// // //             Start Camera
// // //           </button>

// // //         ) : (

// // //           <button
// // //             type="button"
// // //             className="auth-button"
// // //             onClick={verifyFace}
// // //           >
// // //             Verify Face
// // //           </button>

// // //         )}


// // //         <Link
// // //           to="/login"
// // //           className="back-link"
// // //         >
// // //           ← Login with Email
// // //         </Link>

// // //       </div>

// // //     </div>

// // //   );
// // // }

// // // export default FaceLogin;

// // import { useRef, useState } from "react";
// // import { useNavigate, Link } from "react-router-dom";

// // function FaceLogin() {

// //   const videoRef = useRef(null);
// //   const streamRef = useRef(null);

// //   const navigate = useNavigate();

// //   const [cameraStarted, setCameraStarted] = useState(false);
// //   const [error, setError] = useState("");
// //   const [verifying, setVerifying] = useState(false);


// //   // ------------------------------------------------------------
// //   // START CAMERA
// //   // ------------------------------------------------------------

// //   const startCamera = async () => {

// //     try {

// //       setError("");

// //       const stream =
// //         await navigator.mediaDevices.getUserMedia({
// //           video: true
// //         });

// //       streamRef.current = stream;

// //       videoRef.current.srcObject = stream;

// //       setCameraStarted(true);

// //     } catch (err) {

// //       console.error(err);

// //       setError(
// //         "Camera permission is required for face login."
// //       );

// //     }
// //   };


// //   // ------------------------------------------------------------
// //   // STOP CAMERA
// //   // ------------------------------------------------------------

// //   const stopCamera = () => {

// //     if (streamRef.current) {

// //       streamRef.current
// //         .getTracks()
// //         .forEach((track) => track.stop());

// //       streamRef.current = null;

// //     }
// //   };


// //   // ------------------------------------------------------------
// //   // VERIFY FACE
// //   // ------------------------------------------------------------

// //   const verifyFace = async () => {

// //     try {

// //       setError("");
// //       setVerifying(true);

// //       const video = videoRef.current;

// //       if (!video) {

// //         setError("Camera is not available.");

// //         setVerifying(false);

// //         return;
// //       }


// //       // --------------------------------------------------------
// //       // CREATE CANVAS
// //       // --------------------------------------------------------

// //       const canvas =
// //         document.createElement("canvas");

// //       canvas.width = video.videoWidth;
// //       canvas.height = video.videoHeight;


// //       // --------------------------------------------------------
// //       // COPY CURRENT VIDEO FRAME
// //       // --------------------------------------------------------

// //       const context =
// //         canvas.getContext("2d");

// //       context.drawImage(
// //         video,
// //         0,
// //         0,
// //         canvas.width,
// //         canvas.height
// //       );


// //       // --------------------------------------------------------
// //       // CONVERT FRAME TO JPEG
// //       // --------------------------------------------------------

// //       const blob =
// //         await new Promise((resolve) => {

// //           canvas.toBlob(
// //             resolve,
// //             "image/jpeg",
// //             0.9
// //           );

// //         });


// //       if (!blob) {

// //         throw new Error(
// //           "Could not capture camera frame."
// //         );

// //       }


// //       // --------------------------------------------------------
// //       // CREATE FORM DATA
// //       // --------------------------------------------------------

// //       const formData =
// //         new FormData();

// //       formData.append(
// //         "file",
// //         blob,
// //         "face.jpg"
// //       );


// //       // --------------------------------------------------------
// //       // SEND IMAGE TO BACKEND
// //       // --------------------------------------------------------

// //       const response =
// //         await fetch(
// //           "http://127.0.0.1:8000/face/verify",
// //           {
// //             method: "POST",
// //             body: formData
// //           }
// //         );


// //       // --------------------------------------------------------
// //       // CHECK RESPONSE
// //       // --------------------------------------------------------

// //       if (!response.ok) {

// //         throw new Error(
// //           `Server returned ${response.status}`
// //         );

// //       }


// //       const data =
// //         await response.json();


// //       console.log(
// //         "Face verification response:",
// //         data
// //       );


// //       // --------------------------------------------------------
// //       // LOGIN SUCCESS
// //       // --------------------------------------------------------

// //       if (data.verified) {

// //         stopCamera();

// //         navigate("/chat");

// //       }

// //       // --------------------------------------------------------
// //       // LOGIN FAILED
// //       // --------------------------------------------------------

// //       else {

// //         setError(
// //           "Face verification failed. Please try again."
// //         );

// //       }

// //     } catch (err) {

// //       console.error(
// //         "Face verification error:",
// //         err
// //       );

// //       setError(
// //         "Could not connect to the face verification server."
// //       );

// //     } finally {

// //       setVerifying(false);

// //     }
// //   };


// //   // ------------------------------------------------------------
// //   // PAGE
// //   // ------------------------------------------------------------

// //   return (

// //     <div className="auth-page">

// //       <div className="auth-card face-card">

// //         <div className="logo">
// //           RAG<span>CHAT</span>
// //         </div>


// //         <h1>
// //           Face Login
// //         </h1>


// //         <p className="subtitle">
// //           Look directly at the camera to login
// //         </p>


// //         {/* -------------------------------------------------- */}
// //         {/* CAMERA */}
// //         {/* -------------------------------------------------- */}

// //         <div className="camera-container">

// //           {!cameraStarted && (

// //             <div className="camera-placeholder">
// //               📷
// //             </div>

// //           )}


// //           <video
// //             ref={videoRef}
// //             autoPlay
// //             playsInline
// //             className="camera-video"
// //           />

// //         </div>


// //         {/* -------------------------------------------------- */}
// //         {/* ERROR */}
// //         {/* -------------------------------------------------- */}

// //         {error && (

// //           <p className="camera-error">
// //             {error}
// //           </p>

// //         )}


// //         {/* -------------------------------------------------- */}
// //         {/* BUTTON */}
// //         {/* -------------------------------------------------- */}

// //         {!cameraStarted ? (

// //           <button
// //             type="button"
// //             className="auth-button"
// //             onClick={startCamera}
// //           >
// //             Start Camera
// //           </button>

// //         ) : (

// //           <button
// //             type="button"
// //             className="auth-button"
// //             onClick={verifyFace}
// //             disabled={verifying}
// //           >

// //             {verifying
// //               ? "Verifying..."
// //               : "Verify Face"
// //             }

// //           </button>

// //         )}


// //         {/* -------------------------------------------------- */}
// //         {/* BACK TO LOGIN */}
// //         {/* -------------------------------------------------- */}

// //         <Link
// //           to="/login"
// //           className="back-link"
// //           onClick={stopCamera}
// //         >
// //           ← Login with Email
// //         </Link>


// //       </div>

// //     </div>

// //   );

// // }

// // export default FaceLogin;

// import { useState } from "react";
// import { useNavigate, Link } from "react-router-dom";

// function FaceLogin() {

//   const [loggingIn, setLoggingIn] = useState(false);
//   const [message, setMessage] = useState("");
//   const [error, setError] = useState("");

//   const navigate = useNavigate();

//   const loginWithFace = async () => {

//     try {

//       setLoggingIn(true);
//       setError("");
//       setMessage(
//         "Starting Python face recognition camera..."
//       );

//       const response = await fetch(
//         "http://127.0.0.1:8000/face/login",
//         {
//           method: "POST",
//         }
//       );

//       if (!response.ok) {

//         throw new Error(
//           `Server returned ${response.status}`
//         );
//       }

//       const result = await response.json();

//       console.log(
//         "Face login response:",
//         result
//       );

//       if (!result.success) {

//         setError(
//           result.message ||
//           "Face login failed."
//         );

//         setMessage("");
//         setLoggingIn(false);

//         return;
//       }

//       setMessage(
//         `Welcome ${result.username}!`
//       );

//       setLoggingIn(false);

//       setTimeout(() => {
//         navigate("/chat");
//       }, 1000);

//     } catch (err) {

//       console.error(
//         "Face login error:",
//         err
//       );

//       setError(
//         "Could not connect to the face login server."
//       );

//       setMessage("");
//       setLoggingIn(false);
//     }
//   };


//   return (

//     <div className="auth-page">

//       <div className="auth-card face-card">

//         <div className="logo">
//           RAG<span>CHAT</span>
//         </div>

//         <h1>
//           Face Login
//         </h1>

//         <p className="subtitle">
//           Login using your registered face.
//         </p>

//         <div className="camera-container">

//           <div className="camera-placeholder">
//             📷
//           </div>

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

//         <button
//           type="button"
//           className="auth-button"
//           onClick={loginWithFace}
//           disabled={loggingIn}
//         >

//           {loggingIn
//             ? "Face Login Running..."
//             : "Login with Face"}

//         </button>

//         <Link
//           to="/login"
//           className="back-link"
//         >
//           ← Login with Email
//         </Link>

//       </div>

//     </div>
//   );
// }

// export default FaceLogin;

import { useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { API_URL } from "../api";
import { captureFrameAsBlob } from "./FaceCapture.helpers";

function FaceLogin() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const navigate = useNavigate();

  const [cameraStarted, setCameraStarted] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loggingIn, setLoggingIn] = useState(false);

  const startCamera = async () => {
    try {
      setError("");
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      setCameraStarted(true);
    } catch (err) {
      console.error(err);
      setError("Camera permission is required for face login.");
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const loginWithFace = async () => {
    if (!cameraStarted) {
      await startCamera();
      return;
    }

    try {
      setLoggingIn(true);
      setError("");
      setMessage("Verifying your face...");

      const blob = await captureFrameAsBlob(videoRef.current);

      const formData = new FormData();
      formData.append("image", blob, "face.jpg");

      const response = await fetch(`${API_URL}/face/login`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

            if (data.success) {
        setMessage(`Welcome, ${data.name}!`);
        stopCamera();

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("user_name", data.name);
        localStorage.setItem("user_email", data.email);

        setTimeout(() => navigate("/chat"), 800);
      } else {
        setError(data.message || "Face not recognized.");
      }
    } catch (err) {
      console.error(err);
      setError("Could not reach the backend.");
    } finally {
      setLoggingIn(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card face-card">
        <div className="logo">
          RAG<span>CHAT</span>
        </div>

        <h1>Face Login</h1>
        <p className="subtitle">Login using your registered face.</p>

        <div className="camera-container">
          {!cameraStarted && <div className="camera-placeholder">📷</div>}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{ width: "100%", display: cameraStarted ? "block" : "none" }}
          />
        </div>

        {error && <p className="camera-error">{error}</p>}
        {message && <p>{message}</p>}

        <button
          type="button"
          className="auth-button"
          onClick={loginWithFace}
          disabled={loggingIn}
        >
          {!cameraStarted
            ? "Open Camera"
            : loggingIn
            ? "Verifying..."
            : "Login with Face"}
        </button>

        <Link to="/login" className="back-link">
          ← Login with Email
        </Link>
      </div>
    </div>
  );
}

export default FaceLogin;
