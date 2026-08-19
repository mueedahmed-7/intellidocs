import os
import sys
import cv2
import numpy as np
import time
from pathlib import Path

from .config import DATA_DIR, MATCH_COSINE_THRESHOLD, MATCH_L2_THRESHOLD
from .face_utils import (
    init_webcam,
    get_face_detector,
    get_face_recognizer,
    extract_embedding,
    verify_face_embedding
)

def main():
    print("=" * 60)
    print("         PHASE 1: FACE VERIFICATION PROTOTYPE")
    print("=" * 60)

    # 1. Check for registered users
    registered_users = [p.stem for p in DATA_DIR.glob("*.npy")]
    if not registered_users:
        print("[WARNING] No registered faces found in the database.")
        print("Please run face registration first using:")
        print("  python -m member3.face.register_face")
        return

    print("Registered users found:")
    for user in sorted(registered_users):
        print(f" - {user}")
    print("-" * 40)

    # 2. Prompt for username to verify
    target_user = input("Enter username to verify against: ").strip()
    if target_user not in registered_users:
        print(f"[ERROR] User '{target_user}' is not registered.")
        return

    # Load target user's face embedding representation
    user_file = DATA_DIR / f"{target_user}.npy"
    try:
        saved_embedding = np.load(user_file)
        print(f"[INFO] Loaded representation for '{target_user}' (Shape: {saved_embedding.shape})")
    except Exception as e:
        print(f"[ERROR] Failed to load saved face representation: {e}")
        return

    # 3. Initialize webcam and models
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
    print(" - Press [SPACE] to perform face verification.")
    print(" - Press [Q] or [ESC] to exit.")
    print("*" * 50 + "\n")

    last_status = ""
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Webcam feed interrupted.")
            break

        display_frame = frame.copy()
        
        # Face Detection
        retval, faces = detector.detect(frame)
        
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
            status_text = "Press SPACE to Verify"
            status_color = (0, 255, 0) # Green
            if last_status != "one":
                print("[STATUS] Single face detected. Ready. Press [SPACE] to verify.")
                last_status = "one"
            
            # Draw bounding box and landmarks
            face = faces[0]
            x, y, face_w, face_h = map(int, face[0:4])
            cv2.rectangle(display_frame, (x, y), (x + face_w, y + face_h), status_color, 2)
            for idx in range(5):
                lx = int(face[4 + 2 * idx])
                ly = int(face[5 + 2 * idx])
                cv2.circle(display_frame, (lx, ly), 3, (255, 0, 0), -1)
            
            conf = face[14]
            cv2.putText(display_frame, f"Conf: {conf:.2f}", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)

        # Draw HUD info
        cv2.putText(display_frame, f"Target: {target_user}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, f"Status: {status_text}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        cv2.putText(display_frame, "Q: Exit  |  SPACE: Verify", (10, h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Display window
        cv2.imshow("Verify Face (Member 3 Prototype)", display_frame)

        key = cv2.waitKey(1) & 0xFF
        
        # SPACE key to verify
        if key == 32:
            if num_faces == 1:
                print(f"[INFO] Extracting embedding and verifying against '{target_user}'...")
                try:
                    # Extract current face embedding
                    current_embedding = extract_embedding(recognizer, frame, faces[0])
                    
                    # Verify embedding against target user's registered embedding
                    is_match, cos_sim, l2_dist = verify_face_embedding(current_embedding, saved_embedding)
                    
                    # Log details in console
                    print("\n" + "=" * 50)
                    print(f"             VERIFICATION REPORT FOR: {target_user}")
                    print("=" * 50)
                    print(f"Cosine Similarity : {cos_sim:.4f}  (Threshold: >= {MATCH_COSINE_THRESHOLD})")
                    print(f"Euclidean Distance: {l2_dist:.4f}  (Threshold: <= {MATCH_L2_THRESHOLD})")
                    
                    # Prepare overlay window for results
                    result_frame = display_frame.copy()
                    
                    # Determine status visual feedback
                    if is_match:
                        print("RESULT            : MATCH (Identity Verified)")
                        overlay_text = "VERIFIED: MATCH"
                        box_color = (0, 255, 0) # Green
                    else:
                        print("RESULT            : NO MATCH (Verification Failed)")
                        overlay_text = "FAILED: NO MATCH"
                        box_color = (0, 0, 255) # Red
                    print("=" * 50 + "\n")
                    
                    # Draw a nice result banner on the frame
                    # Darken the background slightly for readability
                    overlay = result_frame.copy()
                    cv2.rectangle(overlay, (0, h - 120), (w, h), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.6, result_frame, 0.4, 0, result_frame)
                    
                    # Write results text
                    cv2.putText(result_frame, overlay_text, (20, h - 80), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, box_color, 3)
                    cv2.putText(result_frame, f"Cosine Sim: {cos_sim:.3f} | L2 Dist: {l2_dist:.3f}", 
                                (20, h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(result_frame, "Press any key to close.", (20, h - 15), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
                    
                    # Update window with static frozen frame and wait for user key
                    cv2.imshow("Verify Face (Member 3 Prototype)", result_frame)
                    cv2.waitKey(0) # Wait indefinitely until a key is pressed
                    break
                    
                except Exception as e:
                    print(f"[ERROR] Verification failed: {e}")
                    break
            elif num_faces == 0:
                print("[WARNING] Cannot verify: No face detected.")
            else:
                print("[WARNING] Cannot verify: Multiple faces visible.")
                
        # Q key or ESC to exit
        elif key in [ord('q'), ord('Q'), 27]:
            print("[INFO] Verification cancelled by user.")
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam closed. Verification process finished.")

if __name__ == "__main__":
    main()
