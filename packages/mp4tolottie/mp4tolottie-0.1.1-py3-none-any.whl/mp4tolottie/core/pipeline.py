from .extractor import extract_frames
from .vectorizer import vectorize_frames
from .lottie_builder import create_lottie, save_lottie

def convert(video_path, fps=10, output_path="animation.json"):
    """Convert a video file to a Lottie animation.
    :param video_path: Path to the input video file.
    :param fps: Frames per second for the output animation.
    :param output_path: Path where the output Lottie JSON file will be saved.
    """
    frames = extract_frames(video_path, fps=fps)
    svg_paths = vectorize_frames(frames)
    lottie_data = create_lottie(svg_paths, fps=fps)
    save_lottie(lottie_data, output_path)