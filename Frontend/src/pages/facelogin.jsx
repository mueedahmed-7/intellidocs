import { useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";

function FaceLogin() {

  const videoRef = useRef(null);
  const navigate = useNavigate();

  const [cameraStarted, setCameraStarted] = useState(false);
  const [error, setError] = useState("");

  const startCamera = async () => {

    try {

      setError("");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true
      });

      videoRef.current.srcObject = stream;

      setCameraStarted(true);

    } catch (err) {

      console.error(err);

      setError(
        "Camera permission is required for face login."
      );

    }
  };


  const verifyFace = () => {

    /*
      Face recognition will be connected here later.

      Later:

      1. Capture the user's face
      2. Send it to the backend
      3. Backend compares the face with MongoDB data
      4. Backend returns authentication result
      5. If successful, navigate to /chat
    */

    console.log("Face verification requested");

    // Temporary navigation for frontend testing
    navigate("/chat");
  };


  return (

    <div className="auth-page">

      <div className="auth-card face-card">

        <div className="logo">
          RAG<span>CHAT</span>
        </div>


        <h1>Face Login</h1>


        <p className="subtitle">
          Look directly at the camera to login
        </p>


        <div className="camera-container">

          {!cameraStarted && (

            <div className="camera-placeholder">
              📷
            </div>

          )}


          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="camera-video"
          />

        </div>


        {error && (

          <p className="camera-error">
            {error}
          </p>

        )}


        {!cameraStarted ? (

          <button
            type="button"
            className="auth-button"
            onClick={startCamera}
          >
            Start Camera
          </button>

        ) : (

          <button
            type="button"
            className="auth-button"
            onClick={verifyFace}
          >
            Verify Face
          </button>

        )}


        <Link
          to="/login"
          className="back-link"
        >
          ← Login with Email
        </Link>

      </div>

    </div>

  );
}

export default FaceLogin;