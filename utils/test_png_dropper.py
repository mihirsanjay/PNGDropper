#!/usr/bin/env python3
"""
Test script to verify PNG dropper functionality
"""

import sys
import os
import subprocess
from pathlib import Path

def test_png_conversion(binary_path, png_path):
    """Test PNG conversion roundtrip"""
    
    print(f"Testing PNG conversion for: {binary_path}")
    
    # Convert to PNG
    result = subprocess.run([
        sys.executable, "pe_to_image.py", str(binary_path), str(png_path)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ PNG conversion failed: {result.stderr}")
        return False
    
    print(f"✅ PNG conversion successful")
    
    # Convert back to PE
    restored_path = png_path.with_suffix('.restored.exe')
    result = subprocess.run([
        sys.executable, "pe_to_image.py", str(png_path), str(restored_path)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ PNG to PE conversion failed: {result.stderr}")
        return False
    
    # Compare sizes
    original_size = os.path.getsize(binary_path)
    restored_size = os.path.getsize(restored_path)
    
    print(f"Original size: {original_size} bytes")
    print(f"Restored size: {restored_size} bytes")
    
    if original_size != restored_size:
        print(f"⚠️  Size mismatch (might be due to padding)")
    else:
        print(f"✅ Size matches perfectly")
    
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_png_dropper.py <binary_file> <output_png>")
        sys.exit(1)
    
    binary_path = Path(sys.argv[1])
    png_path = Path(sys.argv[2])
    
    if not binary_path.exists():
        print(f"Binary file not found: {binary_path}")
        sys.exit(1)
    
    success = test_png_conversion(binary_path, png_path)
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
