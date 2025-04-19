from flask import Flask, Response, jsonify, request, send_from_directory, Blueprint
import cv2
import os
from flask_cors import CORS
import threading
from fight_detection import detect_fights, model

app = Flask(__name__)
CORS(app)

# Global variables
detection_running = False
webcam_thread = None

# Create fight blueprint
fight_bp = Blueprint('fight', __name__)

# Ensure directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('static', exist_ok=True)

# --- Webcam-based Fight Detection Route ---
@fight_bp.route('/webcam')
def webcam_detection():
    def generate():
        cap = cv2.VideoCapture(0)  # Start the webcam stream
        if not cap.isOpened():
            yield b'Error: Could not open webcam.'  # Return error if webcam fails
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Use the detect_fights function from fight_detection.py
            annotated_frame = detect_fights(frame)
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        cap.release()  # Release the webcam when done

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- Video-based Fight Detection Route ---
@fight_bp.route('/video', methods=['POST'])
def video_detection():
    video = request.files.get('video')  # Get the uploaded video
    if video is None:
        return "No video file provided", 400

    # Save the uploaded video file
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)  # Ensure the uploads directory exists
    video_path = os.path.join(upload_folder, 'uploaded_fight_video.mp4')
    video.save(video_path)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "Error: Could not open video file", 500

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Default to 30 if FPS is unavailable

    # Prepare the output path for the processed video
    output_folder = 'static'
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, 'fight_output.mp4')

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Define the codec
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Use the detect_fights function from fight_detection.py
        annotated_frame = detect_fights(frame)
        out.write(annotated_frame)

    cap.release()
    out.release()

    # Return the path to the processed video for access via React or frontend
    return jsonify({"message": "Fight video processed successfully", "output_path": output_path})

# --- Webcam Control Routes ---
@fight_bp.route('/webcam/start')
def start_webcam_detection():
    global detection_running, webcam_thread

    if detection_running:
        return jsonify({"status": "already running"})

    detection_running = True
    webcam_thread = threading.Thread(target=run_detection)
    webcam_thread.daemon = True
    webcam_thread.start()

    return jsonify({"status": "started"})

@fight_bp.route('/webcam/stop')
def stop_webcam_detection():
    global detection_running

    if detection_running:
        detection_running = False
        # Give it a moment to clean up
        import time
        time.sleep(1)
        return jsonify({"status": "stopped"})
    else:
        return jsonify({"status": "not running"})

def run_detection():
    """Run fight detection on webcam"""
    global detection_running

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        detection_running = False
        return

    print("Starting webcam detection...")

    while detection_running:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting...")
            break

        # Use the detect_fights function
        frame = detect_fights(frame)

        # Display the resulting frame
        cv2.imshow('Fight Detection', frame)

        # Break the loop with 'q' key
        if cv2.waitKey(1) == ord('q'):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam detection stopped")
    detection_running = False

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Register the blueprint
app.register_blueprint(fight_bp, url_prefix='/fight')

if __name__ == '__main__':
    app.run(debug=True)
