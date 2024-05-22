import cv2
import os

# Function to extract frames from a video
def extract_frames(video_path, output_folder):
    # Open the video file
    video_capture = cv2.VideoCapture(video_path)
    
    # Check if the video opened successfully
    if not video_capture.isOpened():
        print("Error: Could not open video.")
        return
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    frame_count = 0
    
    # Loop through the video and extract frames
    while True:
        ret, frame = video_capture.read()
        
        if not ret:
            break
        
        frame_count += 1
        frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
        
        # Save the frame as an image file
        cv2.imwrite(frame_filename, frame)
    
    video_capture.release()
    # print(f"Frames extracted: {frame_count}")