import cv2
import mediapipe as mp
import uuid
from datetime import datetime
from database import Landmark, Session

session = Session()
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False)
cap = cv2.VideoCapture(0)

save_once = False  # ✅ Only save when 's' is pressed

while True:
    success, frame = cap.read()
    if not success:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape

            # Draw landmarks
            for idx, landmark in enumerate(face_landmarks.landmark):
                x, y = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

            # ✅ Save landmarks only once, on pressing 's'
            if save_once:
                face_id = str(uuid.uuid4())
                for idx, landmark in enumerate(face_landmarks.landmark):
                    x = float(landmark.x * w)
                    y = float(landmark.y * h)
                    landmark_entry = Landmark(
                        id=str(uuid.uuid4()),
                        face_id=face_id,
                        x=x,
                        y=y,
                        timestamp=datetime.utcnow()
                    )
                    session.add(landmark_entry)
                session.commit()
                print(f"✅ Saved 468 landmarks for face ID: {face_id}")
                save_once = False  # Prevent multiple saves

    cv2.imshow("Press 's' to Save Landmarks Once", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        save_once = True  # Trigger save on next face detection

cap.release()
cv2.destroyAllWindows()
