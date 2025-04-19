import cv2
import mediapipe as mp
from scipy.spatial import distance
import numpy as np
import winsound  # For beep sound
import csv
from datetime import datetime

# Define EAR calculation function
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Eye landmark indices from MediaPipe
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# Sensitivity parameters
EYE_AR_THRESH = 0.21
EYE_AR_CONSEC_FRAMES = 10

COUNTER = 0
ALERT_LOGGED = False

# Initialize CSV file for logging
log_file = 'drowsiness_log.csv'
with open(log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Status'])

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

# Start webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        # Get coordinates for eyes
        left_eye = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in LEFT_EYE]
        right_eye = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in RIGHT_EYE]

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        # Draw eyes for visualization
        for (x, y) in left_eye + right_eye:
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # Drowsiness logic
        if ear < EYE_AR_THRESH:
            COUNTER += 1
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                winsound.Beep(1000, 500)  # Beep: 1000 Hz for 0.5 sec
                cv2.putText(frame, "DROWSINESS ALERT!", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

                if not ALERT_LOGGED:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(log_file, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([now, "Drowsy"])
                    ALERT_LOGGED = True
        else:
            COUNTER = 0
            ALERT_LOGGED = False

    # Display frame
    cv2.imshow("Drowsiness Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
