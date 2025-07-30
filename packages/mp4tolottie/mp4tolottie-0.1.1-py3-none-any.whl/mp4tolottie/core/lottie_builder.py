import json

def create_lottie(svg_paths, fps=10):
    """Create a Lottie JSON structure from a list of SVG paths."""
    layers = []
    for i, svg_path in enumerate(svg_paths):
        with open(svg_path, 'r') as f:
            svg_data = f.read()
        layers.append({
            "ddd": 0,
            "ind": i,
            "ty": 0,
            "nm": f"Frame {i}",
            "ks": {},
            "t": {
                "d": {
                    "k": [{"s": {"t": svg_data}, "t": i}]
                }
            }
        })
    return {
        "v": "5.7.4",
        "fr": fps,
        "ip": 0,
        "op": len(svg_paths),
        "w": 512,
        "h": 512,
        "layers": layers
    }

def save_lottie(data, output_file):
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)