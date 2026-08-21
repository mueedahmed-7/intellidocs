// Shared helper for browser-based face capture.
// Used by FaceRegister.jsx and facelogin.jsx.
// Captures a frame from a <video> element into a JPEG Blob,
// which is then POSTed to the backend as multipart/form-data.

export function captureFrameAsBlob(videoElement) {
  return new Promise((resolve, reject) => {
    if (!videoElement) {
      reject(new Error("Video element not available."));
      return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (blob) resolve(blob);
        else reject(new Error("Could not capture frame."));
      },
      "image/jpeg",
      0.92
    );
  });
}
