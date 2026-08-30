import os
import cv2
import math
import numpy as np
from datetime import datetime, timedelta
from pymediainfo import MediaInfo

def format_size(size_in_bytes):
    # Define the suffixes for each size type
    size_bytes = size_in_bytes
    suffixes = ['Byte', 'KB', 'MB', 'GB', 'TB']

    # Determine the appropriate size type
    size_type = 0
    while size_in_bytes >= 1024 and size_type < len(suffixes) - 1:
        size_in_bytes /= 1024
        size_type += 1

    # Format the size with the appropriate suffix
    formatted_size = "{} Bytes ({:.2f} {})".format(size_bytes, size_in_bytes, suffixes[size_type])

    return formatted_size


def extract_info(video_path, num_frames):
    # Get video information using MediaInfo
    media_info = MediaInfo.parse(video_path)
    audio_streams = []
    stream_counter = 1
    video_format = None
    
    for track in media_info.tracks:
        if track.track_type == 'Audio':
            audio_name = track.title if track.title else f"Audio Stream {stream_counter}"
            audio_streams.append({
                'name': audio_name,
                'codec': track.codec_id,
                'bitrate': track.bit_rate,
                'channels': track.channel_s,
                'sample_rate': track.sampling_rate
            })
            stream_counter += 1
        elif track.track_type == 'Video':
            video_format = f"{track.format}"

    vidcap = cv2.VideoCapture(video_path)
    size_in_bytes = float(os.path.getsize(video_path))
    size = format_size(size_in_bytes)
    
    # Video properties
    frame_width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    resolution = f"{int(frame_width)} x {int(frame_height)}"
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    duration = str(datetime.utcfromtimestamp(total_frames / fps).strftime('%H:%M:%S'))
    
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

    # Ensure frames are always in chronological order
    frame_data = sorted(zip(timestamps, frames), key=lambda x: x[0])
    timestamps = [timestamp for timestamp, frame in frame_data]
    frames = [frame for timestamp, frame in frame_data]

    gcd = math.gcd(int(frame_width), int(frame_height))
    aspect_ratio = f"{int(frame_width / gcd)}:{int(frame_height / gcd)}"
    
    video_infos = {
        'resolution': resolution,
        'aspect_ratio': aspect_ratio,
        'fps': fps,
        'duration': duration,
        'codec': video_format
    }
    
    return size, frames, timestamps, video_infos, audio_streams


def add_timestamp(frame, timestamp):
    time_str = str(datetime.utcfromtimestamp(timestamp / 1000).strftime("%H:%M:%S"))
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = min(frame.shape[0], frame.shape[1]) / 500 
    font_thickness = int(min(frame.shape[0], frame.shape[1]) / 200) 
    text_size = cv2.getTextSize(time_str, font, font_scale, font_thickness)[0]
    text_x = 10  # Adjusted to position at the left edge
    text_y = frame.shape[0] - 10
    
    bg_color = (20, 20, 20)
    bg_alpha = 0.4
    overlay = frame.copy()
    cv2.rectangle(overlay, (text_x - 10, text_y - text_size[1] - 10), (text_x + text_size[0] + 10, text_y + 10), bg_color, -1)
    cv2.addWeighted(overlay, bg_alpha, frame, 1 - bg_alpha, 0, frame)
    
    cv2.putText(frame, time_str, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness)
    

def create_collage(frames, timestamps, rows, cols, media_info):
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

    # Add video information within the header
    header_text = [
        '',
        '',
        '',
        f" File: {media_info['filename']}",
        '',
        f" Size: {media_info['size']}",
        '',
        " Audio Info:",
        ''
    ]
    
    for audio_stream in media_info['audio_streams']:
        header_text.append(
            f" - {audio_stream['name']}: Codec: {audio_stream['codec']}, "
            f"Bitrate: {audio_stream['bitrate']} bps, "
            f"Channels: {audio_stream['channels']}, "
            f"Sample Rate: {audio_stream['sample_rate']} Hz"
        )
        header_text.append("")
    
    header_text.extend([
        " Video Info:",
        ''
    ])
    video_info = media_info['video_infos']
    header_text.append(
        f" - Codec: {video_info['codec']}, "
        f"Resolution: {video_info['resolution']}, "
        f"Aspect Ratio: {video_info['aspect_ratio']}, "
        f"Refresh Rate: {video_info['fps']:.0f}fps, "
        f"Duration: {video_info['duration']}"
    )
    header_text.append("")

    # Add black header
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale_value = min(frame.shape[0], frame.shape[1]) / 500
    font_scale = [font_scale_value, font_scale_value, font_scale_value]
    font_thickness_value = int(min(frame.shape[0], frame.shape[1]) / 200) 
    font_thickness = [font_thickness_value, font_thickness_value, font_thickness_value]
    header_height = 0
    line_number = 0
    for line in header_text:
        font_scale.append(font_scale_value)
        font_thickness.append(font_thickness_value)
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
    output_path = os.path.join(output_dir, filename + " [Timeline].jpg")
    cv2.imwrite(output_path, collage)
    print(f"Collage saved for {filename}.")


def process_videos(input_dir, output_dir, rows, cols):
    video_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        
    for video_file in video_files:
        video_path = os.path.join(input_dir, video_file)
        try:                        
            size, frames, timestamps, video_infos, audio_streams = extract_info(video_path, rows * cols)
            media_info = {
                'filename': video_file,
                'size': size,
                'video_infos': video_infos,
                'audio_streams': audio_streams
            }
            
            collage = create_collage(frames, timestamps, rows, cols, media_info)
            save_collage(collage, video_path, output_dir)
        except Exception as e:
            print(f"Error processing {video_file}: {e}")


def main():
    input_dir = os.path.join(os.getcwd(), 'Videos')
    output_dir = os.path.join(os.getcwd(), 'Collages')
    
    rows = None
    cols = None
    
    choice = input('Are these the directories?\n'
                   'Videos: Videos\n'
                   'Collages: Collages\n'
                   ' [Y/N]: ')
    if choice.lower() == 'y':
        os.makedirs(output_dir, exist_ok=True)    
    else:
        input_dir = input("Enter the directory containing all the videos: ")
        output_dir = input("Enter the directory where to save the images: ")
        os.makedirs(output_dir, exist_ok=True)
    

    choice = input('\n'
                   'Option 1:  5 rows and 3 columns \n'
                   'Option 2: 10 rows and 3 columns \n'
                   'Option 3: 13 rows and 3 columns \n'
                   'Default : Custom \n\n'
                   ' > ')

    if choice == '1':
        rows = 5
        cols = 3
    elif choice == '2':
        rows = 10
        cols = 3
    elif choice == '3':
        rows = 13
        cols = 3 
    else:
        rows = int(input("Enter the number of rows for the collage: "))
        cols = int(input("Enter the number of columns for the collage: "))

    process_videos(input_dir, output_dir, rows, cols)


if __name__ == "__main__":
    main()
