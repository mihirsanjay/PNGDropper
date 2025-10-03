#!/usr/bin/env python3
"""
Utility to inspect PNG-embedded malware samples
"""

import sys
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def inspect_png_sample(png_path):
    """Inspect a PNG-embedded malware sample"""
    
    png_path = Path(png_path)
    if not png_path.exists():
        print(f"PNG file not found: {png_path}")
        return
    
    # Load metadata if available
    meta_path = png_path.with_suffix(png_path.suffix + '.meta')
    if meta_path.exists():
        with open(meta_path, 'r') as f:
            original_size = int(f.readline().strip())
            width = int(f.readline().strip())
            height = int(f.readline().strip())
        
        print(f"Metadata found:")
        print(f"  Original binary size: {original_size:,} bytes")
        print(f"  Image dimensions: {width}x{height}")
        print(f"  Total pixels: {width * height:,}")
        print(f"  Padding: {(width * height) - original_size} bytes")
    
    # Load and display image info
    img = Image.open(png_path)
    print(f"\nPNG Image Info:")
    print(f"  Mode: {img.mode}")
    print(f"  Size: {img.size}")
    print(f"  File size: {png_path.stat().st_size:,} bytes")
    
    # Display basic statistics
    img_array = np.array(img)
    print(f"\nPixel Statistics:")
    print(f"  Min value: {img_array.min()}")
    print(f"  Max value: {img_array.max()}")
    print(f"  Mean: {img_array.mean():.2f}")
    print(f"  Std: {img_array.std():.2f}")
    
    # Create a simple ASCII representation
    print(f"\nASCII Preview (top-left 20x10 pixels):")
    preview = img_array[:10, :20]
    for row in preview:
        line = ""
        for pixel in row:
            if pixel < 64:
                line += " "
            elif pixel < 128:
                line += "░"
            elif pixel < 192:
                line += "▒"
            else:
                line += "█"
        print(line)

def main():
    if len(sys.argv) != 2:
        print("Usage: python inspect_png_sample.py <png_file>")
        sys.exit(1)
    
    png_path = sys.argv[1]
    inspect_png_sample(png_path)

if __name__ == "__main__":
    main()