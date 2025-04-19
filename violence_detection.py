import cv2
import mediapipe as mp
import time
import winsound
from ultralytics import YOLO

# Load YOLOv8 model (or adjust with another file if needed)
model = YOLO("yolov8n.pt")

# Initialize MediaPipe Pose model for body movement tracking
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

cap = cv2.VideoCapture(0)  # Use webcam

# Track people and fight detection status
last_positions = {}  # Dictionary to store last shoulder/arm positions for fight detection
fight_detected = False

# Track alert state to avoid continuous beeping
alert_triggered = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame horizontally for mirror effect
    frame = cv2.flip(frame, 1)

    # Get results from YOLO model for object detection
    results = model.predict(source=frame, conf=0.5, save=False, stream=True)

    # Convert frame to RGB for MediaPipe Pose detection
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb_frame)

    people_count = 0
    fight_detected = False  # Flag to track fighting activity

    if result.pose_landmarks:
        # Detect aggressive body movements (check shoulders and arm positions)
        for i in range(len(result.pose_landmarks.landmark)):
            if i == mp_pose.PoseLandmark.LEFT_SHOULDER or i == mp_pose.PoseLandmark.RIGHT_SHOULDER:
                shoulder_position = result.pose_landmarks.landmark[i]
                
                # Store positions to detect fast/aggressive movement
                if shoulder_position.visibility > 0.8:
                    # Check for sudden shoulder position change indicating aggression
                    if i not in last_positions:
                        last_positions[i] = shoulder_position
                    else:
                        last_shoulder = last_positions[i]
                        # Check for a sudden movement threshold (e.g., large distance)
                        if abs(shoulder_position.x - last_shoulder.x) > 0.05 or abs(shoulder_position.y - last_shoulder.y) > 0.05:
                            fight_detected = True
                            last_positions[i] = shoulder_position  # Update last position

    # Iterate through results to track people in the frame
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls = int(box.cls[0])
            name = model.names[cls]

            if name == "person":
                people_count += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # If fighting is detected, trigger alert
    if fight_detected and not alert_triggered:
        alert_triggered = True  # Ensure only one alert is triggered per detection
        frame[:, :, 2] = 255  # Change frame to red for alert
        print("ALERT: Fighting detected!")
        with open("alert_log.txt", "a") as log:
            log.write(f"{time.ctime()} - ALERT: Fighting detected\n")
        winsound.Beep(1000, 500)  # 1000Hz for 500ms as alert sound

    # If multiple people are present but no fighting detected, reset alert state
    if people_count > 2 and not fight_detected:
        alert_triggered = False  # Reset if people are just walking around and not fighting

    # Display the frame with detection
    cv2.imshow("Hostel AI Surveillance", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
