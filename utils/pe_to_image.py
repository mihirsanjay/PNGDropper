#!/usr/bin/env python3
"""
Convert PE binary to PNG image and vice versa
Based on the approach described in the MLSEC paper
"""

import sys
import os
import struct
import math
from PIL import Image
import numpy as np

def pe_to_png(pe_path, png_path):
    """Convert a PE binary to PNG image"""
    
    # Read the binary file
    with open(pe_path, 'rb') as f:
        pe_data = f.read()
    
    pe_size = len(pe_data)
    print(f"Original PE size: {pe_size} bytes")
    
    # Calculate image dimensions
    # We want roughly square images, so calculate width and height
    pixels_needed = pe_size
    width = int(math.ceil(math.sqrt(pixels_needed)))
    height = int(math.ceil(pixels_needed / width))
    
    # Pad the data to fit the image dimensions
    total_pixels = width * height
    padding_needed = total_pixels - pe_size
    pe_data_padded = pe_data + b'\x00' * padding_needed
    
    print(f"Image dimensions: {width}x{height} (total pixels: {total_pixels})")
    print(f"Padding added: {padding_needed} bytes")
    
    # Convert bytes to grayscale image (1 byte per pixel)
    image_array = np.frombuffer(pe_data_padded, dtype=np.uint8).reshape((height, width))
    
    # Create PIL image
    img = Image.fromarray(image_array, mode='L')  # L mode for grayscale
    
    # Save as PNG
    img.save(png_path, 'PNG')
    
    print(f"Saved image to: {png_path}")
    
    # Save metadata file with original size
    metadata_path = png_path + '.meta'
    with open(metadata_path, 'w') as f:
        f.write(f"{pe_size}\n{width}\n{height}\n")
    
    print(f"Metadata saved to: {metadata_path}")
    
    return width, height, pe_size

def png_to_pe(png_path, pe_path, original_size=None):
    """Convert PNG image back to PE binary"""
    
    # Load metadata if available
    metadata_path = png_path + '.meta'
    if os.path.exists(metadata_path) and original_size is None:
        with open(metadata_path, 'r') as f:
            original_size = int(f.readline().strip())
            width = int(f.readline().strip()) 
            height = int(f.readline().strip())
        print(f"Loaded metadata: size={original_size}, dims={width}x{height}")
    
    # Load the PNG image
    img = Image.open(png_path)
    
    # Convert to grayscale if not already
    if img.mode != 'L':
        img = img.convert('L')
    
    # Convert to numpy array and then to bytes
    image_array = np.array(img)
    pe_data = image_array.tobytes()
    
    # Trim to original size if known
    if original_size:
        pe_data = pe_data[:original_size]
    
    # Write the PE file
    with open(pe_path, 'wb') as f:
        f.write(pe_data)
    
    print(f"Restored PE binary to: {pe_path}")
    return len(pe_data)

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Convert PE to PNG: python pe_to_image.py pe_file output.png")
        print("  Convert PNG to PE: python pe_to_image.py input.png output.exe [original_size]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if input_file.endswith('.png'):
        # PNG to PE conversion
        original_size = None
        if len(sys.argv) > 3:
            original_size = int(sys.argv[3])
        png_to_pe(input_file, output_file, original_size)
    else:
        # PE to PNG conversion
        pe_to_png(input_file, output_file)

if __name__ == "__main__":
    main()