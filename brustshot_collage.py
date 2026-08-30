import os
import cv2
import moviepy.editor as mp
import numpy as np
from datetime import datetime

def extract_frames(video_path, num_frames):
    vidcap = cv2.VideoCapture(video_path)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

    timestamps = []
    frames = []

    for idx in frame_indices:
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, image = vidcap.read()
        if not success:
            continue
        frames.append(image)
        timestamp = int(vidcap.get(cv2.CAP_PROP_POS_MSEC))
        timestamps.append(timestamp)

    vidcap.release()
    return frames, timestamps

def add_timestamp(frame, timestamp):
    time_str = str(datetime.utcfromtimestamp(timestamp / 1000).strftime("%H:%M:%S"))
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    font_thickness = 3
    text_size = cv2.getTextSize(time_str, font, font_scale, font_thickness)[0]
    text_x = frame.shape[1] - text_size[0] - 10
    text_y = frame.shape[0] - 10
    cv2.putText(frame, time_str, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness)

def create_collage(frames, timestamps, rows, cols, video_info):
    frame_height, frame_width, _ = frames[0].shape
    collage_height = frame_height * rows
    collage_width = frame_width * cols

    # Create collage
    collage = np.zeros((collage_height, collage_width, 3), dtype=np.uint8)

    # Populate collage with frames
    for i in range(rows):
        for j in range(cols):
            frame_idx = i * cols + j
            if frame_idx < len(frames):
                frame = frames[frame_idx]
                timestamp = timestamps[frame_idx]
                add_timestamp(frame, timestamp)
                collage[i * frame_height: (i + 1) * frame_height, j * frame_width: (j + 1) * frame_width] = frame

    # Add black header
    header_height = 400  # Adjust as needed
    header = np.zeros((header_height, collage_width, 3), dtype=np.uint8)
    header[:] = (0, 0, 0)  # Black color

    # Add video information within the header
    video_info_lines = [
        "",
        "",
        f" Filename: {video_info['filename']}",
        "",
        f" Size: {video_info['size']:.2f} MB",
        "",
        f" Resolution: {video_info['resolution'][0]} x {video_info['resolution'][1]}"
    ]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2.2
    font_thickness = 3
    text_y = 30  # Initial y position
    for line in video_info_lines:
        text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
        text_x = 10
        cv2.putText(header, line, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness)
        text_y += text_size[1] + 5  # Move to next line

    # Combine collage with header
    collage_with_header = np.vstack((header, collage))

    return collage_with_header

def save_collage(collage, video_path, output_dir):
    filename = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(output_dir, filename + "_collage.jpg")
    cv2.imwrite(output_path, collage)
    print(f"Collage saved for {filename}.")

def process_videos(input_dir, output_dir, rows, cols):
    video_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    
    for video_file in video_files:
        video_path = os.path.join(input_dir, video_file)
        video_info = {
            'filename': video_file,
            'size': float(os.path.getsize(video_path)) / (1024.0**2),
            'resolution': mp.VideoFileClip(video_path).size
        }
        
        num_frames = rows * cols
        frames, timestamps = extract_frames(video_path, num_frames)
        collage = create_collage(frames, timestamps, rows, cols, video_info)
        save_collage(collage, video_path, output_dir)

if __name__ == "__main__":
    input_dir = input("Enter the directory containing all the videos: ")
    output_dir = input("Enter the directory where to save the images: ")
    rows = int(input("Enter the number of rows for the collage: "))
    cols = int(input("Enter the number of columns for the collage: "))

    process_videos(input_dir, output_dir, rows, cols)
