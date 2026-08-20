import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

function FaceRegister() {

  const videoRef = useRef(null);

  const [cameraStarted, setCameraStarted] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

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
        "Camera permission is required to complete registration."
      );

    }

  };

  const registerFace = () => {

    console.log("Face registration completed");

    // Backend will be connected here later

    navigate("/login");
  };


  return (

    <div className="auth-page">

      <div className="auth-card face-card">

        <div className="logo">
          RAG<span>CHAT</span>
        </div>

        <h1>Register Your Face</h1>

        <p className="subtitle">
          Face registration is required to complete your account.
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
            className="auth-button"
            onClick={startCamera}
          >
            Start Camera
          </button>

        ) : (

          <button
            className="auth-button"
            onClick={registerFace}
          >
            Register Face
          </button>

        )}

        <p className="required-message">
          Face registration is required before you can continue.
        </p>

      </div>

    </div>

  );
}

export default FaceRegister;