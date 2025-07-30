import os
import subprocess
import shutil

def check_ffmpeg():
    """
    Check if ffmpeg is installed and accessible in the system PATH.
    Raises an error if ffmpeg is not found.
    """
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        raise EnvironmentError("ffmpeg is not installed or not found in the system PATH. Please install ffmpeg.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg command failed: {e}")

def extract_frames(video_path, output_dir="frames", fps=10):
    """
    Extract frames from a video file using ffmpeg.

    :param video_path: Path to the input video file.
    :param output_dir: Directory where extracted frames will be saved.
    :param fps: Frames per second for extraction.
    :return: List of paths to the extracted frame images.
    """
    check_ffmpeg()
    os.makedirs(output_dir, exist_ok=True)
    output_pattern = os.path.join(output_dir, "frame_%04d.png")
    subprocess.run([
        "ffmpeg", "-i", video_path, "-vf", f"fps={fps}", output_pattern
    ], check=True)
    return sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".png")
    ])