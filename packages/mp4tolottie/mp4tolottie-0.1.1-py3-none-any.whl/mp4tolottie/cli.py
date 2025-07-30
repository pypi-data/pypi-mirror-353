import argparse
from mp4tolottie.core.pipeline import convert

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="Path to mp4 file")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second")
    parser.add_argument("--output", default="animation.json", help="Output Lottie file")
    args = parser.parse_args()

    convert(args.video, fps=args.fps, output_path=args.output)

if __name__ == "__main__":
    main()
