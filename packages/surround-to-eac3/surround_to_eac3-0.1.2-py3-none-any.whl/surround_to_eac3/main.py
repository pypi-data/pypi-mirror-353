import subprocess
import os
import shutil
import argparse
import json

def get_stream_info(filepath: str, stream_type: str = "audio") -> list[dict]:
    """
    Retrieves details for specified stream types (audio, video, subtitle) in a file.
    For audio, returns list of dicts with 'index', 'codec_name', 'channels', 'language'.
    For video/subtitle, returns list of dicts with 'index', 'codec_name'.
    """
    if not shutil.which("ffprobe"):
        print(f"    ⚠️ Warning: ffprobe is missing. Cannot get {stream_type} stream info for '{os.path.basename(filepath)}'.")
        return []

    select_streams_option = {
        "audio": "a",
        "video": "v",
        "subtitle": "s"
    }.get(stream_type, "a") # Default to audio if type is unknown

    ffprobe_cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", "-select_streams", select_streams_option, filepath
    ]

    try:
        process = subprocess.run(
            ffprobe_cmd, capture_output=True, text=True, check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if process.returncode != 0:
            # Non-critical error for this function, main processing will decide to skip/fail
            return []
        if not process.stdout.strip():
            return [] # No streams of the selected type found

        data = json.loads(process.stdout)
        streams_details = []
        for stream in data.get("streams", []):
            detail = {
                "index": stream["index"], # Absolute stream index
                "codec_name": stream.get("codec_name", "unknown")
            }
            if stream_type == "audio":
                detail["channels"] = stream.get("channels")
                detail["language"] = stream.get("tags", {}).get("language", "und").lower()
            streams_details.append(detail)
        return streams_details
    except json.JSONDecodeError:
        print(f"    ⚠️ Warning: Failed to decode ffprobe JSON for {stream_type} streams in '{os.path.basename(filepath)}'.")
        return []
    except Exception as e:
        print(f"    ⚠️ Error getting {stream_type} stream info for '{os.path.basename(filepath)}': {e}")
        return []

def process_file_with_ffmpeg(
    input_filepath: str,
    output_dir_for_file: str | None,
    audio_bitrate: str,
    audio_processing_ops: list[dict] # [{'index':X, 'op':'transcode'/'copy', 'lang':'eng'}]
) -> str | None:
    """
    Processes a single video file using ffmpeg with detailed stream mapping.
    """
    if not shutil.which("ffmpeg"):
        print("    🚨 Error: ffmpeg is not installed or not found.") # Should be caught earlier too
        return None

    base_filename = os.path.basename(input_filepath)
    name, ext = os.path.splitext(base_filename)
    output_filename = f"{name}_eac3{ext}" # Suffix remains as per original request

    if output_dir_for_file:
        if not os.path.isdir(output_dir_for_file):
            try:
                os.makedirs(output_dir_for_file, exist_ok=True)
            except OSError as e:
                print(f"    🚨 Error creating output directory '{output_dir_for_file}': {e}")
                return None
        final_output_filepath = os.path.join(output_dir_for_file, output_filename)
    else:
        final_output_filepath = os.path.join(os.path.dirname(input_filepath), output_filename)

    if os.path.abspath(input_filepath) == os.path.abspath(final_output_filepath):
        print(f"    ⚠️ Warning: Input and output file paths are identical ('{input_filepath}'). Skipping.")
        return None

    ffmpeg_cmd = ["ffmpeg", "-i", input_filepath]
    map_operations = []
    output_audio_stream_ffmpeg_idx = 0 # For -c:a:0, -c:a:1 etc.

    # Map Video Streams (optional mapping)
    map_operations.extend(["-map", "0:v?", "-c:v", "copy"])
    # Map Subtitle Streams (optional mapping)
    map_operations.extend(["-map", "0:s?", "-c:s", "copy"])

    # Map Audio Streams based on operations
    for op_details in audio_processing_ops:
        input_stream_map_specifier = f"0:{op_details['index']}" # Map by original ffprobe index
        map_operations.extend(["-map", input_stream_map_specifier])

        if op_details['op'] == 'transcode':
            map_operations.extend([f"-c:a:{output_audio_stream_ffmpeg_idx}", "eac3"])
            map_operations.extend([f"-b:a:{output_audio_stream_ffmpeg_idx}", audio_bitrate])
            map_operations.extend([f"-ac:a:{output_audio_stream_ffmpeg_idx}", "6"])
            map_operations.extend([f"-metadata:s:a:{output_audio_stream_ffmpeg_idx}", f"language={op_details['lang']}"])
        elif op_details['op'] == 'copy':
            map_operations.extend([f"-c:a:{output_audio_stream_ffmpeg_idx}", "copy"])
        # 'drop' operations are handled by not including them in audio_processing_ops sent here

        output_audio_stream_ffmpeg_idx += 1
    
    ffmpeg_cmd.extend(map_operations)
    ffmpeg_cmd.extend(["-y", final_output_filepath])

    # print(f"       Executing: {' '.join(ffmpeg_cmd)}") # For debugging complex commands
    print(f"    ⚙️ Processing: '{base_filename}' -> '{output_filename}'")

    try:
        process = subprocess.run(
            ffmpeg_cmd, capture_output=True, text=True, check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if process.returncode == 0:
            if os.path.exists(final_output_filepath) and os.path.getsize(final_output_filepath) > 0:
                print(f"    ✅ Success: '{os.path.basename(final_output_filepath)}' saved.")
                return final_output_filepath
            else: # Should not happen if ffmpeg returncode is 0 and no "-f null" output.
                print(f"    ⚠️ Warning: ffmpeg reported success for '{base_filename}', but output file is missing or empty.")
                if process.stderr: print(f"       ffmpeg stderr:\n{process.stderr}")
                return None
        else:
            print(f"    🚨 Error during ffmpeg processing for '{base_filename}'. RC: {process.returncode}")
            # if process.stdout: print(f"       ffmpeg stdout:\n{process.stdout}") # Usually not much on error
            if process.stderr: print(f"       ffmpeg stderr:\n{process.stderr.strip()}")
            if os.path.exists(final_output_filepath):
                try: os.remove(final_output_filepath)
                except OSError: pass
            return None
    except Exception as e:
        print(f"    🚨 An unexpected error occurred during transcoding of '{base_filename}': {e}")
        return None


def main():
    # Initial check for ffmpeg and ffprobe
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        missing_tools = []
        if not shutil.which("ffmpeg"): missing_tools.append("ffmpeg")
        if not shutil.which("ffprobe"): missing_tools.append("ffprobe")
        print(f"🚨 Error: {', '.join(missing_tools)} is not installed or not found in your system's PATH. Please install ffmpeg.")
        return

    parser = argparse.ArgumentParser(
        description="Advanced video transcoder: E-AC3 for specific audio, language filtering, folder processing.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the input video file or folder.",
        dest="input_path"
    )
    parser.add_argument(
        "-o", "--outdir",
        help="Optional. Base directory to save processed files.\n"
             "If input is a folder, source structure is replicated under this directory.\n"
             "If not set, processed files are saved alongside originals.",
        dest="output_directory_base",
        default=None
    )
    parser.add_argument(
        "-br", "--bitrate",
        help="Audio bitrate for E-AC3 (e.g., '640k', '1536k'). Defaults to '1536k'.",
        dest="audio_bitrate",
        default="1536k"
    )

    args = parser.parse_args()
    input_path_abs = os.path.abspath(args.input_path)
    files_to_process_paths = []

    # Collect all files to process
    if os.path.isdir(input_path_abs):
        print(f"📁 Scanning folder: {input_path_abs}")
        for root, _, filenames in os.walk(input_path_abs):
            for filename in filenames:
                if filename.lower().endswith((".mkv", ".mp4")):
                    files_to_process_paths.append(os.path.join(root, filename))
        if not files_to_process_paths:
            print("    No .mkv or .mp4 files found in the specified folder.")
    elif os.path.isfile(input_path_abs):
        if input_path_abs.lower().endswith((".mkv", ".mp4")):
            files_to_process_paths.append(input_path_abs)
        else:
            print(f"⚠️ Provided file '{args.input_path}' is not an .mkv or .mp4 file. Skipping this input.")
    else:
        print(f"🚨 Error: Input path '{args.input_path}' is not a valid file or directory.")
        return

    if not files_to_process_paths:
        print("No files to process.")
        return

    print(f"\nFound {len(files_to_process_paths)} file(s) to potentially process...")
    # Initialize stats counters
    stats = {"processed": 0, "skipped_rules": 0, "failed": 0}

    for filepath in files_to_process_paths:
        # Determine a display name relative to the initial input path for cleaner logs
        if os.path.isdir(input_path_abs):
            display_name = os.path.relpath(filepath, input_path_abs)
        else: # Single file input
            display_name = os.path.basename(filepath)
            
        print(f"\n▶️ Checking: '{display_name}'")

        audio_streams_details = get_stream_info(filepath, "audio")
        audio_ops_for_ffmpeg = [] # List of audio operations for ffmpeg

        if not audio_streams_details:
            print("    ℹ️ No audio streams found in this file.")
        else:
            for stream in audio_streams_details:
                lang = stream['language']
                op_to_perform = None # Will be 'transcode', 'copy', or None (for drop)

                if lang in ['eng', 'jpn']:
                    is_5_1 = stream.get('channels') == 6
                    is_not_ac3_eac3 = stream.get('codec_name') not in ['ac3', 'eac3']

                    if is_5_1 and is_not_ac3_eac3:
                        op_to_perform = 'transcode'
                        print(f"    🔈 Will transcode: Audio stream #{stream['index']} ({lang}, {stream.get('channels')}ch, {stream.get('codec_name')})")
                    else:
                        op_to_perform = 'copy'
                        reason_parts = []
                        if stream.get('codec_name') in ['ac3', 'eac3']: reason_parts.append(f"already {stream.get('codec_name')}")
                        if stream.get('channels') != 6: reason_parts.append(f"not 5.1 ({stream.get('channels')}ch)")
                        reason = ", ".join(reason_parts) if reason_parts else "meets other criteria for copying"
                        print(f"    🔈 Will copy: Audio stream #{stream['index']} ({lang}, {stream.get('channels')}ch, {stream.get('codec_name')}) - Reason: {reason}")
                else:
                    # Language is not English or Japanese, so it will be dropped (no op_to_perform)
                    print(f"    🔈 Will drop: Audio stream #{stream['index']} ({lang}, {stream.get('channels')}ch, {stream.get('codec_name')}) - Other language.")

                if op_to_perform:
                    audio_ops_for_ffmpeg.append({
                        'index': stream['index'],
                        'op': op_to_perform,
                        'lang': lang # Store for potential metadata setting during transcode
                    })
        
        # --- Apply the new skipping logic ---
        # If no English/Japanese audio streams meet criteria for processing (transcode/copy),
        # skip creating a new file for this input file entirely.
        if not audio_ops_for_ffmpeg:
            print(f"    ⏭️ Skipping '{display_name}': No English/Japanese audio streams meet criteria for processing (transcode/copy). File will not be created.")
            stats["skipped_rules"] += 1
            continue # Move to the next file in files_to_process_paths

        # If we reach here, audio_ops_for_ffmpeg is NOT empty,
        # meaning at least one English or Japanese audio stream will be processed.

        # Determine the output directory for this specific file
        output_dir_for_this_file = None
        if args.output_directory_base:
            if os.path.isdir(input_path_abs): # Input was a folder
                # Replicate source structure from input_path_abs root into output_directory_base
                relative_dir_of_file = os.path.relpath(os.path.dirname(filepath), start=input_path_abs)
                if relative_dir_of_file == ".": # file is in the root of input_path_abs
                    output_dir_for_this_file = args.output_directory_base
                else:
                    output_dir_for_this_file = os.path.join(args.output_directory_base, relative_dir_of_file)
            else: # Input was a single file, output_directory_base is the direct output dir
                output_dir_for_this_file = args.output_directory_base
        # If args.output_directory_base is None, output_dir_for_this_file remains None,
        # and process_file_with_ffmpeg will save the output alongside the original file.

        processed_file_path = process_file_with_ffmpeg(
            filepath,
            output_dir_for_this_file,
            args.audio_bitrate,
            audio_ops_for_ffmpeg # This list is guaranteed to be non-empty here
        )

        if processed_file_path:
            stats["processed"] += 1
        else:
            stats["failed"] += 1
            # Detailed error message for the specific file would have been printed by process_file_with_ffmpeg

    # Print summary of operations
    print("\n--- Processing Summary ---")
    print(f"Total files checked: {len(files_to_process_paths)}")
    print(f"Successfully processed: {stats['processed']}")
    print(f"Skipped (no qualifying audio ops): {stats['skipped_rules']}")
    print(f"Failed to process: {stats['failed']}")
    print("--------------------------")
