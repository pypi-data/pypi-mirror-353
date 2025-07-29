# Surround to E-AC3 Transcoder (eac3-transcode)

**A** command-line utility to intelligently find and convert 5.1 surround sound audio tracks in your video files (`.mkv`, `.mp4`) to **the E-AC3 (Dolby Digital Plus) format, while preserving other streams.**

This tool is perfect for users who want to standardize their media library's audio, ensuring compatibility and high quality for 5.1 channel audio tracks, particularly for English and Japanese languages.

## Overview

`eac3-transcode` automates the often tedious process of inspecting video files, identifying specific audio tracks, and re-encoding them. It's designed to be smart about which tracks to process:

* **Scans Individual Files or Entire Directories:** Process a single video or batch-process an entire folder (including subfolders).

* **Targets Specific Languages:** Focuses on English (`eng`) and Japanese (`jpn`) audio streams.

* **Intelligent Transcoding:**

  * Converts 5.1 channel audio streams (that aren't already `ac3` or `eac3`) to `eac3`.

* **Smart Copying:**

  * Copies English or Japanese audio streams that are already in `ac3` or `eac3` format.

  * Copies English or Japanese audio streams that are not 5.1 channels (e.g., stereo).

* **Stream Preservation:**

  * Video streams are always copied without re-encoding (lossless).

  * Subtitle streams are always copied without re-encoding.

* **Efficient Processing:**

  * Other language audio streams are dropped to save space and processing time.

  * Files are skipped entirely if no English or Japanese audio streams meet the criteria for transcoding or copying, preventing empty or unnecessary output files.

* **Flexible Output:** Save processed files alongside originals or in a specified output directory, maintaining the source folder structure if applicable.

## Prerequisites

Before you can use `eac3-transcode`, you **must** have **FFmpeg** installed on your system and accessible in your system's PATH. FFmpeg is used for both analyzing (ffprobe) and processing (ffmpeg) the video files.

* **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows) and add the `bin` directory to your system's PATH.

* **macOS:** Install via Homebrew: `brew install ffmpeg`

* **Linux:** Install using your distribution's package manager (e.g., `sudo apt update && sudo apt install ffmpeg` for Debian/Ubuntu).

You can verify your FFmpeg installation by opening a terminal or command prompt and typing `ffmpeg -version` and `ffprobe -version`.

## Installation

Install `eac3-transcode` directly from PyPI using pip:

pip install surround-to-eac3
It's recommended to install it in a virtual environment.

## Usage

The primary command is `eac3-transcode`.

### Basic Examples:

1. **Process a single video file (output saved in the same directory):**

eac3-transcode --input "/path/to/your/movie.mkv"
*Output will be `/path/to/your/movie_eac3.mkv` if processing occurs.*

2. **Process** all videos in a folder (output saved in the same directory as **originals):**

eac3-transcode --input "/path/to/your/video_folder/"

3. **Process videos and save them to a specific output directory:**

eac3-transcode --input "/path/to/your/video_folder/" --outdir "/path/to/your/processed_videos/"
*If `/path/to/your/video_folder/` contains subfolders, the structure will be replicated under `/path/to/your/processed_videos/`.*

4. **Specify a different bitrate for transcoded E-AC3 audio:**

eac3-transcode --input "video.mp4" --bitrate "640k"

## Command-Line Options

**Usage:**

eac3-transcode [-h] -i INPUT_PATH [-o OUTPUT_DIRECTORY_BASE] [-br AUDIO_BITRATE]  
An advanced video transcoder that processes files to use E-AC3 for specific audio tracks, filters by language, and can process entire folders.

**Options:**

* `-h, --help`  
    Show this help message and exit.

* `-i INPUT_PATH, --input INPUT_PATH`  
    **(Required)** Path to the input video file or folder.

* `-o OUTPUT_DIRECTORY_BASE, --outdir OUTPUT_DIRECTORY_BASE`  
    **(Optional)** Base directory to save processed files. If the input is a folder, the original source structure is replicated under this directory. If this option is not set, processed files will be saved alongside the original files.

* `-br AUDIO_BITRATE, --bitrate AUDIO_BITRATE`  
    **(Optional)** Sets the audio bitrate for the E-AC3 stream (e.g., '640k', '1536k'). Defaults to '1536k'.

## How It Works

1. **File Discovery:** The script scans the input path for `.mkv` and `.mp4` files.

2. **Stream Analysis (using `ffprobe`):** For each file:

   * It extracts information about all audio streams: codec, channels, and language tags.

3. **Decision Logic:**

   * **Language Filter:** Only `eng` (English) and `jpn` (Japanese) audio streams are considered for keeping. Others are marked to be dropped.

   * **Transcode Criteria:** An `eng` or `jpn` stream is transcoded to E-AC3 if:

     * It has 6 audio channels (5.1 surround).

     * Its current codec is *not* `ac3` or `eac3`.

   * **Copy Criteria:** An `eng` or `jpn` stream is copied directly if:

     * It's already `ac3` or `eac3`.

     * It does not have 6 channels (e.g., it's stereo).

   * **File Skipping:** If no audio streams are marked for either 'transcode' or 'copy' (e.g., a file only contains French audio, or all English/Japanese audio is already in the desired format and channel layout for copying), the entire file is skipped to avoid creating redundant or empty output files.

4. **Processing (using `ffmpeg`):**

   * A new FFmpeg command is constructed based on the decisions.

   * Video (`-c:v copy`) and subtitle (`-c:s copy`) streams are mapped and copied directly.

   * Selected audio streams are mapped and either transcoded to `eac3` with the specified bitrate (and forced to 6 channels) or copied (`-c:a copy`).

   * Language metadata is set for transcoded audio streams.

   * The output file is named by appending `_eac3` to the original filename (before the extension).

## Troubleshooting

* `ffmpeg` or **`ffprobe` not found:**

  * Ensure FFmpeg is installed correctly and its `bin` directory is in your system's PATH environment variable. See the [Prerequisites](#prerequisites) section.

* **No files processed / "Skipping 'filename': No English/Japanese audio streams meet criteria..."**:

  * This is expected behavior if the files scanned do not contain any English or Japanese audio tracks that require transcoding to E-AC3 or qualify for copying based on the tool's logic. For example, if a file only has a stereo English AAC track, it will be copied (not transcoded to 5.1 E-AC3). If it only has a French 5.1 DTS track, it will be skipped.

* **Permission Errors:**

  * Ensure you have write permissions for the output directory and read permissions for the input files/directory.

* **Unexpected FFmpeg errors:**

  * The script prints FFmpeg's stderr output on failure, which can provide clues. Ensure your video files are not corrupted.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://gitea.jono-rams.work/jono/ffmpeg-audio-transcoder/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](https://gitea.jono-rams.work/jono/ffmpeg-audio-transcoder/src/branch/main/LICENSE) file for details.

## Acknowledgements

* This tool relies heavily on the fantastic [FFmpeg](https://ffmpeg.org/) project.
