import os
from PIL import Image
import subprocess

def check_portrace():
    """
    Check if Portrace is installed and accessible in the system PATH.
    Raises an error if Potrace is not found.
    """
    try:
        subprocess.run(["potrace", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        raise EnvironmentError("Potrace is not installed or not found in the system PATH. Please install Portrace.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Potrace command failed: {e}")

def convert_to_svg(png_path, svg_path):
    """
    Convert a PNG image to SVG format using Portrace.
    :param png_path: Path to the input PNG image.
    :param svg_path: Path where the output SVG file will be saved.
    """
    bmp_path = png_path.replace(".png", ".bmp")
    print(f"Attempting to open PNG: {png_path}")
    Image.open(png_path).convert("L").save(bmp_path)
    subprocess.run(["potrace", bmp_path, "-s", "-o", svg_path], check=True)
    os.remove(bmp_path)

def vectorize_frames(png_paths, output_dir="svgs"):
    """
    Vectorize a list of PNG images to SVG format.
    :param png_path: Path to PNG images to be vectorized.
    :param output_dir: Directory where the output SVG files will be saved.
    :return: List of paths to the generated SVG files.
    """
    check_portrace()
    os.makedirs(output_dir, exist_ok=True)
    svg_paths = []
    for png in png_paths:
        svg = os.path.join(output_dir, os.path.basename(png).replace(".png", ".svg"))
        convert_to_svg(png, svg)
        svg_paths.append(svg)
    return svg_paths

if __name__ == "__main__":
    png_path = r"D:\Projects\MP4_to_Lottie\assets\extracted_frames"
    output_dir = r"D:\Projects\MP4_to_Lottie\assets\vectorized_svgs"
    png_paths = [os.path.join(png_path, f) for f in os.listdir(png_path) if f.endswith(".png")]
    svg_files = vectorize_frames(png_paths, output_dir)
    print(f"Vectorized {len(svg_files)} frames to {output_dir}.")