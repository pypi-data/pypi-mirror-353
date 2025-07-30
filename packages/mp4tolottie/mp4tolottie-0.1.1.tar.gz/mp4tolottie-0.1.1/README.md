# 🎞️ mp4tolottie

Convert MP4 video clips into lightweight Lottie animations automatically — frame-by-frame, vectorized, and optimized.

---

## 🚀 Features

- 🎥 Extract frames from MP4 videos using `ffmpeg`
- 🖼️ Convert raster frames to vector graphics (`SVG`) using `potrace`
- 📦 Generate optimized Lottie JSON animation
- 🧩 CLI interface for ease of use
- 🔧 Modular design for customization

---

## 📦 Installation

Install via PyPI:

```bash
pip install mp4tolottie
```

---

## ⚙️ Requirements

`mp4tolottie` depends on the following system tools:

### ✅ FFmpeg

Install FFmpeg and ensure it's accessible in your system's `PATH`.

#### macOS:
```bash
brew install ffmpeg
```

#### Ubuntu / Debian:
```bash
sudo apt update && sudo apt install ffmpeg
```

#### Windows:
1. Download from [ffmpeg.org/download](https://ffmpeg.org/download.html)
2. Extract the ZIP
3. Add the `bin/` folder to your System PATH

---

### ✅ Potrace

`potrace` is required to vectorize raster images into SVGs.

#### macOS:
```bash
brew install potrace
```

#### Ubuntu / Debian:
```bash
sudo apt install potrace
```

#### Windows:
Download from [potrace.sourceforge.net](http://potrace.sourceforge.net) and add it to PATH.
