import os
import sys
import re
import cv2
import numpy as np
from pathlib import Path

from .config import DATA_DIR
from .face_utils import (
    init_webcam,
    get_face_detector,
    get_face_recognizer,
    extract_embedding
)

def clean_username(username: str) -> str:
    """Sanitizes username to ensure it is a safe filename."""
    return re.sub(r'[^a-zA-Z0-9_\-]', '', username)

def main():
    print("=" * 60)
    print("         PHASE 1: FACE REGISTRATION PROTOTYPE")
    print("=" * 60)
    
    # 1. Prompt for username
    raw_user = input("Enter unique username/ID to register: ").strip()
    username = clean_username(raw_user)
    
    if not username:
        print("[ERROR] Invalid username. Use alphanumeric characters only.")
        return
        
    user_file = DATA_DIR / f"{username}.npy"
    if user_file.exists():
        confirm = input(f"[WARNING] User '{username}' already exists. Overwrite? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Registration cancelled.")
            return

    # 2. Initialize models and webcam
    print("\n[INFO] Starting camera and loading models... Please wait.")
    try:
        cap = init_webcam(0)
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    # Warm up camera & get dimensions
    ret, frame = cap.read()
    if not ret or frame is None:
        print("[ERROR] Failed to grab frame from webcam during initialization.")
        cap.release()
        return

    h, w, c = frame.shape
    try:
        detector = get_face_detector(w, h)
        recognizer = get_face_recognizer()
    except Exception as e:
        print(f"[ERROR] Failed to load models: {e}")
        cap.release()
        return

    print("\n" + "*" * 50)
    print("              WEBCAM CONTROLS")
    print(" - Show exactly ONE face in the camera frame.")
    print(" - Press [SPACE] to capture and register face.")
    print(" - Press [Q] or [ESC] to exit and cancel.")
    print("*" * 50 + "\n")

    last_status = ""
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Webcam feed interrupted.")
            break

        # Make a copy for display annotation
        display_frame = frame.copy()
        
        # Face Detection
        # YuNet returns (retval, faces)
        retval, faces = detector.detect(frame)
        
        # Determine number of faces detected
        num_faces = 0
        if faces is not None:
            num_faces = faces.shape[0]

        status_text = ""
        status_color = (0, 0, 255) # Red default
        
        if num_faces == 0:
            status_text = "No face detected. Waiting..."
            status_color = (0, 165, 255) # Orange
            if last_status != "zero":
                print("[STATUS] No face detected. Waiting...")
                last_status = "zero"
        elif num_faces > 1:
            status_text = "Multiple faces! Show only ONE face."
            status_color = (0, 0, 255) # Red
            if last_status != "multiple":
                print("[STATUS] Multiple faces detected! Please ensure only one person is visible.")
                last_status = "multiple"
        else: # num_faces == 1
            status_text = "Press SPACE to Register"
            status_color = (0, 255, 0) # Green
            if last_status != "one":
                print("[STATUS] Single face detected. Ready to register. Press [SPACE].")
                last_status = "one"
            
            # Draw bounding box and landmarks for the detected face
            face = faces[0]
            # Bounding box
            x, y, face_w, face_h = map(int, face[0:4])
            cv2.rectangle(display_frame, (x, y), (x + face_w, y + face_h), status_color, 2)
            
            # Landmarks: right eye, left eye, nose tip, right mouth corner, left mouth corner
            # landmarks start at index 4 with x,y pairs
            for idx in range(5):
                lx = int(face[4 + 2 * idx])
                ly = int(face[5 + 2 * idx])
                cv2.circle(display_frame, (lx, ly), 3, (255, 0, 0), -1)
                
            # Confidence score
            conf = face[14]
            cv2.putText(display_frame, f"Conf: {conf:.2f}", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)

        # Draw HUD status info
        cv2.putText(display_frame, f"User: {username}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, f"Status: {status_text}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        cv2.putText(display_frame, "Q: Exit  |  SPACE: Register", (10, h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Display window
        cv2.imshow("Register Face (Member 3 Prototype)", display_frame)

        # Key event handling
        key = cv2.waitKey(1) & 0xFF
        
        # SPACE key to capture
        if key == 32:
            if num_faces == 1:
                # Capture the face embedding
                print(f"[INFO] Capturing face embedding for '{username}'...")
                try:
                    # Extract 128-D SFace embedding
                    embedding = extract_embedding(recognizer, frame, faces[0])
                    
                    # Save local face representation ONLY (No raw photographs saved)
                    np.save(user_file, embedding)
                    print(f"[SUCCESS] Face representation saved locally to: {user_file}")
                    print(f"[INFO] Embedding shape: {embedding.shape}")
                    break
                except Exception as e:
                    print(f"[ERROR] Failed to extract or save face representation: {e}")
                    break
            elif num_faces == 0:
                print("[WARNING] Cannot register: No face detected.")
            else:
                print("[WARNING] Cannot register: Multiple faces visible.")
                
        # Q key or ESC to exit
        elif key in [ord('q'), ord('Q'), 27]:
            print("[INFO] Registration cancelled by user.")
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam closed. Registration process finished.")

if __name__ == "__main__":
    main()
