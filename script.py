import argparse
import os
import sys
import subprocess
import urllib.request


def download_file(url, output_name):
    """
    Downloads a file from the given URL and saves it locally under the provided output name.
    
    Args:
        url (str): The URL of the file to download.
        output_name (str): The base name for the downloaded file (without extension).

    Returns:
        str: The path to the downloaded input file.
    """
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/58.0.3029.110 Safari/537.3'
        )
    }
    req = urllib.request.Request(url, headers=headers)
    input_file = f"{output_name}.in"

    with urllib.request.urlopen(req) as response:
        total_size = int(response.getheader('Content-Length').strip())
        bytes_downloaded = 0
        chunk_size = 1024  # Chunk size for reading the response
        last_percent_reported = 0

        # Open local file for writing the downloaded data
        with open(input_file, 'wb') as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                bytes_downloaded += len(chunk)

                percent_downloaded = bytes_downloaded / total_size * 100
                if int(percent_downloaded) >= last_percent_reported + 1:
                    last_percent_reported = int(percent_downloaded)
                    print(f"Downloaded: {bytes_downloaded} / {total_size} bytes ({percent_downloaded:.2f}%)", flush=True)

    print(f"\nDownloaded file saved as: {input_file}", flush=True)
    return input_file

def process_file(input_file, audio_bit, vid_quality, output_name, vfr_enabled):
    """
    Processes a downloaded video file using ffmpeg, applying audio/video settings and optional VFR mode.
    
    Args:
        input_file (str): Path to the downloaded input file.
        audio_bit (str): Audio bitrate (e.g. '128k').
        vid_quality (str): CRF value for video quality (lower is better, e.g. '23').
        output_name (str): Base name for the output file.
        vfr_enabled (bool): Whether to enable variable frame rate (VFR) mode.

    Returns:
        str: Path to the processed output file.
    """
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)

    file_name_without_ext = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, f"{file_name_without_ext}.mp4")

    print(f"Processing {input_file} with ffmpeg...", flush=True)

    ffmpeg_command = [
        'ffmpeg', '-i', input_file,
        '-c:v', 'libx264',
        '-preset', 'veryslow',
        '-crf', vid_quality,
        '-c:a', 'aac',
        '-b:a', audio_bit
    ]

    if vfr_enabled:
        ffmpeg_command.extend(['-vsync', 'vfr'])

    ffmpeg_command.append(output_file)

    print(f"\nRunning ffmpeg command: {ffmpeg_command}", flush=True)
    subprocess.run(ffmpeg_command)

    print(f"Processed file saved as: {output_file}", flush=True)
    return output_file


# Get input data
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a video file and process it using FFmpeg.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--url', metavar='URL', help='URL of the video to download (or use --file)')
    parser.add_argument('--file', metavar='PATH', help='Path for file to process')
    parser.add_argument('--qa', metavar='BITRATE', required=True, help='Audio bitrate (e.g. 96k)')
    parser.add_argument('--qv', metavar='CRF', required=True, help='Video CRF quality (lower = better, e.g. 27)')
    parser.add_argument('--output', metavar='NAME', required=True, help='Base name for the output file')
    parser.add_argument('--vfr', action='store_true', help='Enable Variable Frame Rate mode (VFR)')
    
    args = parser.parse_args()

    # Determine input file
    if args.url:
        input_file = download_file(args.url, args.output)

    # Use local file
    elif args.file:
        input_file = args.file 

    # No input specified
    else: 
        print("Error: You must specify either --url or --file.", file=sys.stderr)
        sys.exit(1)

    # Start file processing
    processed_file = process_file(input_file, a_bit, vid_q, out_n, vfr_e)
