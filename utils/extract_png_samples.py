#!/usr/bin/env python3
"""
Extract PNG samples from dropper DLLs for inspection and analysis
"""

import os
import struct
from pathlib import Path

def extract_png_from_dll(dll_path, output_png_path):
    """Extract PNG resource from dropper DLL"""
    print(f"Extracting PNG from {dll_path}")
    
    with open(dll_path, 'rb') as f:
        # Read the entire DLL
        dll_data = f.read()
        
        # Look for PNG signature - find the real PNG (not false positive)
        png_signature = b'\x89PNG\r\n\x1a\n'
        png_start = -1
        
        # Find all PNG signatures and pick the one followed by IHDR
        start_pos = 0
        while True:
            pos = dll_data.find(png_signature, start_pos)
            if pos == -1:
                break
                
            # Check if this is followed by IHDR chunk (real PNG)
            ihdr_check = dll_data[pos + 8:pos + 12]
            if ihdr_check == b'IHDR' or dll_data[pos + 12:pos + 16] == b'IHDR':
                png_start = pos
                break
            start_pos = pos + 1
            
        if png_start == -1:
            print(f"  ❌ No valid PNG found in {dll_path}")
            return False
            
        print(f"  🎯 PNG found at offset: {png_start} (0x{png_start:x})")
        
        # Find PNG end (IEND chunk + CRC)
        iend_signature = b'IEND'
        iend_pos = dll_data.find(iend_signature, png_start)
        
        if iend_pos == -1:
            print(f"  ❌ PNG IEND not found")
            return False
            
        # PNG ends 4 bytes after IEND signature (CRC32)
        png_end = iend_pos + len(iend_signature) + 4
        
        # Extract PNG data
        png_data = dll_data[png_start:png_end]
        print(f"  📏 PNG size: {len(png_data)} bytes")
        
        # Save PNG
        with open(output_png_path, 'wb') as png_file:
            png_file.write(png_data)
            
        print(f"  ✅ PNG extracted to: {output_png_path}")
        return True

def analyze_png_properties(png_path):
    """Analyze PNG properties"""
    try:
        from PIL import Image
        import numpy as np
        
        print(f"\n📊 Analyzing {png_path}:")
        
        with Image.open(png_path) as img:
            width, height = img.size
            mode = img.mode
            
            print(f"  📐 Dimensions: {width} x {height} = {width*height:,} pixels")
            print(f"  🎨 Mode: {mode}")
            
            # Convert to numpy array to analyze pixel values
            if mode == 'L':  # Grayscale
                pixels = np.array(img)
                print(f"  📈 Pixel value range: {pixels.min()} - {pixels.max()}")
                print(f"  📊 Mean pixel value: {pixels.mean():.1f}")
                
                # Check if it looks like PE data (should start with MZ = 0x4D, 0x5A = 77, 90)
                first_pixels = pixels.flatten()[:16]
                print(f"  🔍 First 16 pixel values: {first_pixels}")
                
                if len(first_pixels) >= 2 and first_pixels[0] == 77 and first_pixels[1] == 90:
                    print(f"  ✅ PE signature detected! (MZ = 77, 90)")
                else:
                    print(f"  ⚠️  No PE signature in first pixels")
                    
    except Exception as e:
        print(f"  ❌ Analysis failed: {e}")

def main():
    """Extract and analyze PNG samples"""
    print("🔍 PNG Sample Extraction and Analysis")
    print("=" * 50)
    
    # Paths
    dropper_dir = Path("png_droppers_no_encoding")
    inspection_dir = Path("png_samples_inspection")
    
    if not dropper_dir.exists():
        print(f"❌ Dropper directory not found: {dropper_dir}")
        return
    
    # Get first 5 dropper DLLs for analysis
    dll_files = sorted(list(dropper_dir.glob("dropper_*.dll")))[:5]
    
    if not dll_files:
        print(f"❌ No dropper DLLs found in {dropper_dir}")
        return
        
    print(f"📂 Found {len(dll_files)} dropper DLLs, analyzing first 5...")
    
    # Extract PNGs from each DLL
    for i, dll_path in enumerate(dll_files, 1):
        print(f"\n[{i}/5] Processing {dll_path.name}")
        
        # Extract PNG
        png_name = dll_path.stem + ".png"  # dropper_1.dll -> dropper_1.png
        png_output_path = inspection_dir / png_name
        
        if extract_png_from_dll(dll_path, png_output_path):
            # Analyze extracted PNG
            analyze_png_properties(png_output_path)
    
    print(f"\n🎉 Extraction complete! PNGs saved to: {inspection_dir}/")
    print(f"📝 Files created:")
    for png_file in sorted(inspection_dir.glob("*.png")):
        size_kb = png_file.stat().st_size / 1024
        print(f"  📄 {png_file.name}: {size_kb:.1f} KB")

if __name__ == "__main__":
    main()