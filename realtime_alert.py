import cv2
import mediapipe as mp
import time
import winsound
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# MediaPipe pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize video capture
cap = cv2.VideoCapture(0)

# Fight detection variables
prev_positions = None
movement_threshold = 0.3  # Less sensitive (adjust if needed)
aggression_counter = 0
aggression_threshold = 5  # Must detect aggressive movement for 5 frames
cooldown_time = 5  # seconds
last_alert_time = 0

def detect_aggressive_movement(landmarks, prev_positions):
    try:
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    except:
        return False, prev_positions

    if prev_positions:
        prev_left, prev_right = prev_positions
        left_move = abs(left_shoulder.y - prev_left)
        right_move = abs(right_shoulder.y - prev_right)

        if left_move > movement_threshold or right_move > movement_threshold:
            prev_positions = (left_shoulder.y, right_shoulder.y)
            return True, prev_positions

    prev_positions = (left_shoulder.y, right_shoulder.y)
    return False, prev_positions

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    results = model.predict(source=frame, conf=0.5, save=False, stream=True)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pose_result = pose.process(rgb)

    fight_detected = False

    if pose_result.pose_landmarks:
        aggressive, prev_positions = detect_aggressive_movement(pose_result.pose_landmarks.landmark, prev_positions)
        if aggressive:
            aggression_counter += 1
        else:
            aggression_counter = max(0, aggression_counter - 1)

        if aggression_counter >= aggression_threshold:
            current_time = time.time()
            if current_time - last_alert_time > cooldown_time:
                fight_detected = True
                last_alert_time = current_time
                aggression_counter = 0  # reset counter

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            name = model.names[cls]
            if name == "person":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    if fight_detected:
        frame[:, :, 2] = 255  # Red tint
        print("⚠️ ALERT: Fighting Detected!")
        with open("alert_log.txt", "a") as log:
            log.write(f"{time.ctime()} - ALERT: Fighting detected\n")
        winsound.Beep(1000, 500)

    cv2.imshow("Hostel Surveillance", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()