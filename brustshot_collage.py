import os
import cv2
import moviepy.editor as mp
import numpy as np
from tqdm import tqdm
from datetime import datetime
import math


def format_size(size_in_bytes):
    # Define the suffixes for each size type
    suffixes = ['Byte', 'KB', 'MB', 'GB', 'TB']

    # Determine the appropriate size type
    size_type = 0
    while size_in_bytes >= 1024 and size_type < len(suffixes) - 1:
        size_in_bytes /= 1024
        size_type += 1

    # Format the size with the appropriate suffix
    formatted_size = "{:.2f} {}".format(size_in_bytes, suffixes[size_type])

    return formatted_size


def extract_info(video_path, num_frames):
    vidcap = cv2.VideoCapture(video_path)
    size_in_bytes = float(os.path.getsize(video_path))
    size = format_size(size_in_bytes)
    resolution = mp.VideoFileClip(video_path).size
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = vidcap.get(cv2.CAP_PROP_FPS)  # Frames per second
    duration = total_frames / fps  # Video duration in seconds
    frame_width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    gcd = math.gcd(int(frame_width), int(frame_height))
    aspect_ratio = f"{int(frame_width / gcd)}:{int(frame_height / gcd)}"
    
    frame_indices = np.linspace(fps * 30, total_frames - fps * 30, num_frames, dtype=int)  # Adjusting timestamps

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
    return size, resolution, frames, timestamps, duration, aspect_ratio, fps


def add_timestamp(frame, timestamp, duration):
    time_str = str(datetime.utcfromtimestamp(timestamp / 1000).strftime("%H:%M:%S"))
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    font_thickness = 3
    text_size = cv2.getTextSize(time_str, font, font_scale, font_thickness)[0]
    text_x = frame.shape[1] - text_size[0] - 10
    text_y = frame.shape[0] - 10
    
    bg_color = (20, 20, 20)
    bg_alpha = 0.4
    overlay = frame.copy()
    cv2.rectangle(overlay, (text_x - 10, text_y - text_size[1] - 10), (text_x + text_size[0] + 10, text_y + 10), bg_color, -1)
    cv2.addWeighted(overlay, bg_alpha, frame, 1 - bg_alpha, 0, frame)
    
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
                add_timestamp(frame, timestamp, video_info['duration'])
                collage[i * frame_height: (i + 1) * frame_height, j * frame_width: (j + 1) * frame_width] = frame

    # Add video information within the header
    header_text = [
        '',
        '',
        f" File: {video_info['filename']}",
        '',
        f"   Size: {video_info['size']}",
        '',
        f"   Duration: {datetime.utcfromtimestamp(video_info['duration']).strftime('%H:%M:%S')}",
        '',
        f"   Resolution: {video_info['resolution'][0]} x {video_info['resolution'][1]}",
        '',
        f"   FPS: {video_info['fps']:.1f}",
        '',
        f"   Aspect Ratio: {video_info['aspect_ratio']}",
        ''
    ]

    # Add black header
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = [2.2, 2.2, 3.2]
    font_thickness = [3, 3, 5]
    header_height = 0
    line_number = 0
    for line in header_text:
        font_scale.append(2.2)
        font_thickness.append(3)
        text_size = cv2.getTextSize(line, font, font_scale[line_number], font_thickness[line_number])[0]
        header_height += text_size[1] + 5  # Add height for the current line
        line_number = line_number + 1

    header = np.zeros((header_height, collage_width, 3), dtype=np.uint8)
    header[:] = (50, 50, 50)  # Black color

    text_y = 30  # Initial y position
    line_number = 0
    for line in header_text:
        text_size = cv2.getTextSize(line, font, font_scale[line_number], font_thickness[line_number])[0]
        text_x = 10
        cv2.putText(header, line, (text_x, text_y), font, font_scale[line_number], (255, 255, 255), font_thickness[line_number])
        text_y += text_size[1] + 5  # Move to next line
        line_number = line_number + 1

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
        try:                        
            size, resolution, frames, timestamps, duration, aspect_ratio, fps = extract_info(video_path, rows * cols)
            video_info = {
                'filename': video_file,
                'size': size,
                'resolution': resolution,
                'duration': duration,
                'aspect_ratio': aspect_ratio,
                'fps': fps,
            }
            
            collage = create_collage(frames, timestamps, rows, cols, video_info)
            save_collage(collage, video_path, output_dir)
        except Exception as e:
            print(f"Error processing {video_file}: {e}")


def main():
    input_dir = None
    output_dir = None
    rows = None
    cols = None
    
    choice = input('Are these the directories?\n'
                   'Videos: Videos\n'
                   'Collages: Collages\n'
                   ' [Y/N]: ')
    if choice.lower() == 'y':
        input_dir = os.path.join(os.getcwd(), 'Videos')
        output_dir = os.path.join(os.getcwd(), 'Collages')
        # Create directories if they don't exist
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
    else:
        input_dir = input("Enter the directory containing all the videos: ")
        output_dir = input("Enter the directory where to save the images: ")
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    choice = input('13 rows and 3 columns, right?\n'
                   ' [Y/N]: ')
    if choice.lower() == 'y':
        rows = 13
        cols = 3
    else:
        rows = int(input("Enter the number of rows for the collage: "))
        cols = int(input("Enter the number of columns for the collage: "))

    process_videos(input_dir, output_dir, rows, cols)


if __name__ == "__main__":
    main()
