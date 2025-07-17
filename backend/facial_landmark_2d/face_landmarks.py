import cv2
import mediapipe as mp
import time
import os

# MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

# Output directory
output_dir = "snapshots"
os.makedirs(output_dir, exist_ok=True)

# Webcam
cap = cv2.VideoCapture(0)

# Button settings
button_size = (100, 50)
button_gap = 20
buttons = [
    {"label": "Save", "color": (0, 255, 0), "action": "save"},
    {"label": "Retake", "color": (255, 255, 0), "action": "retake"},
    {"label": "Quit", "color": (0, 0, 255), "action": "quit"},
]
button_positions = []  # Will be updated dynamically

# Clicked action
clicked_action = None

# Check if click is inside a button
def get_clicked_button(x, y):
    for i, (bx, by) in enumerate(button_positions):
        bw, bh = button_size
        if bx <= x <= bx + bw and by <= y <= by + bh:
            return buttons[i]["action"]
    return None

# Mouse callback
def mouse_callback(event, x, y, flags, param):
    global clicked_action
    if event == cv2.EVENT_LBUTTONDOWN:
        action = get_clicked_button(x, y)
        if action:
            clicked_action = action

cv2.namedWindow("Facial Landmarks")
cv2.setMouseCallback("Facial Landmarks", mouse_callback)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    # Detect landmarks
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    results = face_mesh.process(image_rgb)
    image_rgb.flags.writeable = True
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    h, w, _ = image.shape
    landmark_points = []

    # Draw landmarks
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, landmark in enumerate(face_landmarks.landmark):
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(image, (x, y), radius=1, color=(0, 255, 0), thickness=-1)
                landmark_points.append((idx, x, y))

    # Compute dynamic button positions (centered)
    total_width = len(buttons) * button_size[0] + (len(buttons) - 1) * button_gap
    x_start = (w - total_width) // 2
    y_pos = h - button_size[1] - 10
    button_positions = []

    # Draw buttons
    for i, button in enumerate(buttons):
        bx = x_start + i * (button_size[0] + button_gap)
        by = y_pos
        button_positions.append((bx, by))

        cv2.rectangle(image, (bx, by), (bx + button_size[0], by + button_size[1]), button["color"], -1)
        cv2.putText(image, button["label"], (bx + 10, by + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # Show image
    cv2.imshow("Facial Landmarks", image)

    key = cv2.waitKey(5) & 0xFF
    if key == 27 or clicked_action == "quit":
        break

    # Save using 's' key or button
    if (key == ord('s') or clicked_action == "save") and landmark_points:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        image_filename = os.path.join(output_dir, f"snapshot_{timestamp}.png")
        data_filename = os.path.join(output_dir, f"landmarks_{timestamp}.csv")

        cv2.imwrite(image_filename, image)
        with open(data_filename, 'w') as f:
            f.write("id,x,y\n")
            for idx, x, y in landmark_points:
                f.write(f"{idx},{x},{y}\n")

        print(f"[✔] Saved image: {image_filename}")
        print(f"[✔] Saved landmarks: {data_filename}")
        clicked_action = None

    # Retake: do nothing, skip saving
    if clicked_action == "retake":
        print("[🔄] Retake pressed. Frame ignored.")
        clicked_action = None

cap.release()
cv2.destroyAllWindows()
