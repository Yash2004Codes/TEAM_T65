from ultralytics import YOLO
import cv2
import time

# Load your trained model
model = YOLO('best.pt')  # adjust path to your trained weights


# Function for webcam inference
def webcam_detection():
    # Open webcam (0 is usually the default camera)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    while True:
        # Read frame from webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break
        
        # Run inference on the frame
        results = model(frame)
        
        # Visualize the results on the frame
        annotated_frame = results[0].plot()
        
        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the webcam and close all windows
    cap.release()
    cv2.destroyAllWindows()

# Function for video file inference
def video_detection(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Create a VideoWriter object to save the output video
    output_path = 'output_detection.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    while True:
        # Read frame from the video
        ret, frame = cap.read()
        if not ret:
            print("End of video file")
            break
        
        # Run YOLOv8 inference on the frame
        results = model(frame)
        
        # Visualize the results on the frame
        annotated_frame = results[0].plot()
        
        # Write the frame to output video
        out.write(annotated_frame)
        
        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Choose which function to run
# For webcam:
#webcam_detection()

# For video file (uncomment and provide your video path):
 video_detection('/path/to/your/video.mp4')