# Video Timeline Collage Generator

A Python utility that scans a directory of videos, extracts representative frames from each video, overlays their timestamps, and combines them into a single timeline-style collage.

## Table of Contents

- [Features](#features)
- [Example](#example)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Windows](#windows)
  - [Linux](#linux)
  - [macOS](#macos)
- [Directory Structure](#directory-structure)
- [Usage](#usage)
- [Collage Layouts](#collage-layouts)
  - [Option 1](#option-1)
  - [Option 2](#option-2)
  - [Option 3](#option-3)
- [Generated Files](#generated-files)
- [Metadata](#metadata)
  - [File](#file)
  - [Audio](#audio)
  - [Video](#video)
- [Timestamp Sampling](#timestamp-sampling)
- [Frame Order](#frame-order)
- [Supported Video Formats](#supported-video-formats)
- [Error Handling](#error-handling)
- [Notes](#notes)
  - [Large Videos](#large-videos)
  - [Memory Usage](#memory-usage)
  - [Duration](#duration)
- [Customization](#customization)
  - [Sampling Margin](#sampling-margin)
  - [Timestamp Appearance](#timestamp-appearance)
  - [Output Filename](#output-filename)
- [Troubleshooting](#troubleshooting)
  - [`cv2` ModuleNotFoundError](#cv2-modulenotfounderror)
  - [`pymediainfo` ModuleNotFoundError](#pymediainfo-modulenotfounderror)
  - [MediaInfo Errors](#mediainfo-errors)
  - [Video Cannot Be Opened](#video-cannot-be-opened)
  - [Frames Appear in the Wrong Order](#frames-appear-in-the-wrong-order)
- [License](#license)

---

[(ToC)](#table-of-contents)
## Features

- Extracts evenly distributed frames from each video.
- Avoids sampling the first and last 30 seconds of the video.
- Adds timestamps to extracted frames.
- Creates configurable row × column collages.
- Displays video metadata in the header.
- Displays audio stream information.
- Calculates the video's aspect ratio.
- Supports custom input and output directories.
- Saves each collage as a JPEG image.
- Processes multiple videos in a directory.
- Automatically creates the output directory.

---

[(ToC)](#table-of-contents)
## Example

For a video, selecting a `5 × 3` collage produces 15 representative frames:

```text
┌──────────────┬──────────────┬──────────────┐
│    Frame 1   │    Frame 2   │    Frame 3   │
├──────────────┼──────────────┼──────────────┤
│    Frame 4   │    Frame 5   │    Frame 6   │
├──────────────┼──────────────┼──────────────┤
│    Frame 7   │    Frame 8   │    Frame 9   │
├──────────────┼──────────────┼──────────────┤
│   Frame 10   │   Frame 11   │   Frame 12   │
├──────────────┼──────────────┼──────────────┤
│   Frame 13   │   Frame 14   │   Frame 15   │
└──────────────┴──────────────┴──────────────┘
```

---

[(ToC)](#table-of-contents)
## Requirements

- Python 3.8+
- OpenCV
- NumPy
- pymediainfo
- MediaInfo

---

[(ToC)](#table-of-contents)
## Installation

Install the required Python packages:

    pip install opencv-python numpy pymediainfo

`pymediainfo` also requires the MediaInfo library to be installed on your system.

### Windows

Download and install MediaInfo from:

https://mediaarea.net/en/MediaInfo

### Linux

On Debian/Ubuntu:

    sudo apt install mediainfo

Then install the Python dependencies:

    pip install opencv-python numpy pymediainfo

### macOS

Using Homebrew:

    brew install mediainfo

Then:

    pip install opencv-python numpy pymediainfo

---

[(ToC)](#table-of-contents)
## Directory Structure

By default, the script expects:

    Project/
    ├── script.py
    ├── Videos/
    │   ├── video1.mp4
    │   ├── video2.mkv
    │   └── video3.mov
    └── Collages/

The `Collages` directory is automatically created if it does not exist.

---

[(ToC)](#table-of-contents)
## Usage

Run the script:

    python script.py

The program asks whether you want to use the default directories:

    Are these the directories?
    Videos: Videos
    Collages: Collages
     [Y/N]:

Enter `Y` to use the default directories.

Otherwise, enter custom paths when prompted.

---

[(ToC)](#table-of-contents)
## Collage Layouts

The script provides three predefined layouts:

    Option 1:  5 rows and 3 columns
    Option 2: 10 rows and 3 columns
    Option 3: 13 rows and 3 columns
    Default : Custom

### Option 1

`5 × 3 = 15 frames`

### Option 2

`10 × 3 = 30 frames`

### Option 3

`13 × 3 = 39 frames`

Selecting any other option allows you to specify the number of rows and columns manually.

For example:

    Enter the number of rows for the collage: 8
    Enter the number of columns for the collage: 4

This produces a collage containing `8 × 4 = 32 frames`.

---

[(ToC)](#table-of-contents)
## Generated Files

For a source video:

    Videos/example.mp4

the generated collage is saved as:

    Collages/example [Timeline].jpg

---

[(ToC)](#table-of-contents)
## Metadata

The collage header contains information about the source video and its audio streams.

### File

- Filename
- File size

### Audio

For each audio stream:

- Stream name
- Codec
- Bitrate
- Number of channels
- Sample rate

### Video

- Codec
- Resolution
- Aspect ratio
- FPS
- Duration

Example:

    File: example.mp4

    Size: 123456789 Bytes (117.74 MB)

    Audio Info:

    - Audio Stream 1: Codec: AAC, Bitrate: 192000 bps,
      Channels: 2, Sample Rate: 48000 Hz

    Video Info:

    - Codec: AVC, Resolution: 1920 x 1080,
      Aspect Ratio: 16:9, Refresh Rate: 30fps,
      Duration: 01:20:35

---

[(ToC)](#table-of-contents)
## Timestamp Sampling

The script samples frames between 30 seconds after the beginning and 30 seconds before the end of the video.

This prevents the collage from being dominated by opening or closing frames.

The number of sampled frames is determined by:

    num_frames = rows * cols

For example, a `5 × 3` collage extracts 15 frames.

---

[(ToC)](#table-of-contents)
## Frame Order

Frames are intended to appear chronologically from left to right and then top to bottom.

For a `5 × 3` layout:

    01  02  03
    04  05  06
    07  08  09
    10  11  12
    13  14  15

The timestamp displayed on each frame makes it easy to verify the chronological order.

---

[(ToC)](#table-of-contents)
## Supported Video Formats

The script relies on OpenCV and MediaInfo. Supported formats therefore depend on the codecs available in your OpenCV/FFmpeg and MediaInfo installations.

Common formats include:

- MP4
- MKV
- AVI
- MOV
- WebM
- MPEG
- MPG

---

[(ToC)](#table-of-contents)
## Error Handling

If a video cannot be processed, the script reports the error and continues with the next video.

Example:

    Error processing example.mp4: <error message>

This prevents a single problematic video from stopping the entire batch.

---

[(ToC)](#table-of-contents)
## Notes

### Large Videos

High-resolution videos can produce very large collage images because the original frame dimensions are retained.

For example, a `13 × 3` collage made from 4K frames can result in a very large JPEG.

### Memory Usage

The script keeps extracted frames in memory while creating the collage.

Increasing the number of rows and columns therefore increases memory usage.

### Duration

The duration is calculated using:

    total_frames / fps

Videos with unusual or variable frame-rate characteristics may not always produce a perfectly accurate duration.

---

[(ToC)](#table-of-contents)
## Customization

### Sampling Margin

The script currently excludes approximately 30 seconds from the beginning and end of each video.

The relevant calculation is:

    fps * 30

To exclude one minute instead:

    fps * 60

### Timestamp Appearance

The `add_timestamp()` function controls:

- Font
- Font size
- Font thickness
- Position
- Background color
- Background transparency
- Text color

### Output Filename

The output naming convention is controlled by the `save_collage()` function.

The default format is:

    <video filename> [Timeline].jpg

---

[(ToC)](#table-of-contents)
## Troubleshooting

### `cv2` ModuleNotFoundError

Install OpenCV:

    pip install opencv-python

### `pymediainfo` ModuleNotFoundError

Install pymediainfo:

    pip install pymediainfo

### MediaInfo Errors

Make sure the MediaInfo library/application is installed and accessible on your system.

### Video Cannot Be Opened

Check whether OpenCV can decode the video's codec.

If necessary, convert the video to a commonly supported format such as H.264 MP4.

### Frames Appear in the Wrong Order

Frames should be extracted using ascending frame indices.

If necessary, ensure the extracted frame/timestamp pairs are sorted chronologically before creating the collage.

---

[(ToC)](#table-of-contents)
## License

This project is provided as-is for personal or internal use.
