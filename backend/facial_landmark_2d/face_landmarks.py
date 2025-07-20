import cv2
import mediapipe as mp
import time
import os
import numpy as np
from datetime import datetime
from backend.database.db import session
from backend.database.models import Snapshot

# MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

# Output dir
output_dir = "snapshots"
os.makedirs(output_dir, exist_ok=True)

# Webcam
cap = cv2.VideoCapture(0)

# Modes
mode = "camera"  # "camera" or "viewer"
clicked_action = None
button_size = (100, 50)
button_gap = 20
button_positions = []

# Buttons
camera_buttons = [
    {"label": "Save", "color": (0, 255, 0), "action": "save"},
    {"label": "Retake", "color": (255, 255, 0), "action": "retake"},
    {"label": "View Saved", "color": (0, 255, 255), "action": "view"},
    {"label": "Quit", "color": (0, 0, 255), "action": "quit"},
]
viewer_buttons = [
    {"label": "Back", "color": (200, 200, 200), "action": "back"},
]

# Mouse Events
def get_clicked_button(x, y):
    for i, (bx, by) in enumerate(button_positions):
        bw, bh = button_size
        if bx <= x <= bx + bw and by <= y <= by + bh:
            if mode == "camera":
                return camera_buttons[i]["action"]
            elif mode == "viewer":
                return viewer_buttons[i]["action"]
    return None

def mouse_callback(event, x, y, flags, param):
    global clicked_action
    if event == cv2.EVENT_LBUTTONDOWN:
        action = get_clicked_button(x, y)
        if action:
            clicked_action = action

cv2.namedWindow("Facial Landmarks")
cv2.setMouseCallback("Facial Landmarks", mouse_callback)

while True:
    if mode == "camera":
        success, image = cap.read()
        if not success:
            continue

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image_rgb)
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        h, w, _ = image.shape
        landmark_points = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
                    landmark_points.append((idx, x, y))

        # Draw buttons
        total_width = len(camera_buttons) * button_size[0] + (len(camera_buttons) - 1) * button_gap
        x_start = (w - total_width) // 2
        y_pos = h - button_size[1] - 10
        button_positions = []
        for i, button in enumerate(camera_buttons):
            bx = x_start + i * (button_size[0] + button_gap)
            by = y_pos
            button_positions.append((bx, by))
            cv2.rectangle(image, (bx, by), (bx + button_size[0], by + button_size[1]), button["color"], -1)
            cv2.putText(image, button["label"], (bx + 8, by + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        cv2.imshow("Facial Landmarks", image)

        key = cv2.waitKey(5) & 0xFF
        if key == 27 or clicked_action == "quit":
            break
        elif (key == ord("s") or clicked_action == "save") and landmark_points:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            img_path = os.path.join(output_dir, f"snapshot_{timestamp}.png")
            csv_path = os.path.join(output_dir, f"landmarks_{timestamp}.csv")
            cv2.imwrite(img_path, image)
            with open(csv_path, 'w') as f:
                f.write("id,x,y\n")
                for idx, x, y in landmark_points:
                    f.write(f"{idx},{x},{y}\n")
            snapshot = Snapshot(image_path=img_path, landmark_csv=csv_path)
            session.add(snapshot)
            session.commit()
            print(f"[✔] Saved {img_path} and DB record")
            clicked_action = None
        elif clicked_action == "retake":
            clicked_action = None
        elif clicked_action == "view":
            mode = "viewer"
            clicked_action = None

    elif mode == "viewer":
        snapshots = session.query(Snapshot).order_by(Snapshot.timestamp.desc()).all()
        if not snapshots:
            viewer_image = 255 * np.ones((400, 600, 3), dtype=np.uint8)
            cv2.putText(viewer_image, "No snapshots found.", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        else:
            thumbs_per_row = 4
            thumb_size = (150, 100)
            spacing = 20
            rows = (len(snapshots) + thumbs_per_row - 1) // thumbs_per_row
            viewer_image = 255 * np.ones(((thumb_size[1] + spacing) * rows + 100, (thumb_size[0] + spacing) * thumbs_per_row, 3), dtype=np.uint8)

            for i, snap in enumerate(snapshots[:12]):
                try:
                    img = cv2.imread(snap.image_path)
                    if img is None:
                        continue
                    thumb = cv2.resize(img, thumb_size)
                    row = i // thumbs_per_row
                    col = i % thumbs_per_row
                    x = col * (thumb_size[0] + spacing)
                    y = row * (thumb_size[1] + spacing)
                    viewer_image[y:y+thumb_size[1], x:x+thumb_size[0]] = thumb
                except:
                    continue

        # Draw Back button
        h, w, _ = viewer_image.shape
        total_width = len(viewer_buttons) * button_size[0]
        x_start = (w - total_width) // 2
        y_pos = h - button_size[1] - 10
        button_positions = []
        for i, button in enumerate(viewer_buttons):
            bx = x_start + i * (button_size[0] + button_gap)
            by = y_pos
            button_positions.append((bx, by))
            cv2.rectangle(viewer_image, (bx, by), (bx + button_size[0], by + button_size[1]), button["color"], -1)
            cv2.putText(viewer_image, button["label"], (bx + 10, by + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        cv2.imshow("Facial Landmarks", viewer_image)
        key = cv2.waitKey(5) & 0xFF
        if key == 27 or clicked_action == "back":
            mode = "camera"
            clicked_action = None

cap.release()
cv2.destroyAllWindows()
