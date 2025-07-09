import cv2
import mediapipe as mp

# ✅ Correct 68-point mapping for nose, eyes, lips, brows, jawline
LANDMARK_68_IDS = [
    234, 93, 132, 58, 172, 136, 150, 149, 176,
    148, 152, 377, 400, 378, 379, 365, 397,
    70, 63, 105, 66, 107,
    336, 296, 334, 293, 300,
    168, 6, 197, 195,
    5, 4, 1, 19, 94,
    33, 160, 158, 133, 153, 144,
    362, 385, 387, 263, 373, 380,
    78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415,
    82, 81, 80, 191, 80, 95, 88, 178
]

# 🎯 Initialize Mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False)
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx in LANDMARK_68_IDS:
                if idx < len(face_landmarks.landmark):
                    h, w, _ = frame.shape
                    point = face_landmarks.landmark[idx]
                    x, y = int(point.x * w), int(point.y * h)
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

    cv2.imshow('Face Mesh - 68 Key Landmarks', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
