# detector.py

import cv2
import mediapipe as mp
from .db import Landmark, session

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False)

def detect_and_store():
    cap = cv2.VideoCapture(0)
    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks_list = []
                for lm in face_landmarks.landmark:
                    h, w, _ = frame.shape
                    x, y = int(lm.x * w), int(lm.y * h)
                    landmarks_list.append({'x': x, 'y': y})

                # Store in DB
                landmark_entry = Landmark(coordinates=landmarks_list)
                session.add(landmark_entry)
                session.commit()
                print(f"Stored {len(landmarks_list)} landmarks.")

                # Draw on face
                for point in landmarks_list:
                    cv2.circle(frame, (point['x'], point['y']), 1, (0, 255, 0), -1)

        cv2.imshow("Facial Landmarks", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
