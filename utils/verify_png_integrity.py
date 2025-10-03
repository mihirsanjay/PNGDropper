#!/usr/bin/env python3
"""
Hash verification utility for PNG-embedded malware samples
"""

import sys
import os
import subprocess
import hashlib
from pathlib import Path

def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def verify_png_conversion_integrity():
    """Verify integrity of all PNG converted samples"""
    
    source_dir = Path("/home/mihir/Downloads/to_be_evaded_ds_unpacked")
    png_dir = Path("/home/mihir/Dropper/png_embedded_samples")
    utils_dir = Path("/home/mihir/Dropper/utils")
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return False
    
    if not png_dir.exists():
        print(f"❌ PNG samples directory not found: {png_dir}")
        return False
    
    # Find all PNG files
    png_files = list(png_dir.glob("*.png"))
    if not png_files:
        print("❌ No PNG files found to verify")
        return False
    
    print(f"🔍 Verifying {len(png_files)} PNG-converted samples...")
    print("=" * 80)
    
    all_passed = True
    
    for png_file in png_files:
        sample_name = png_file.stem  # Remove .png extension
        original_file = source_dir / sample_name
        
        if not original_file.exists():
            print(f"⚠️  Original file not found for {sample_name}")
            continue
        
        # Convert PNG back to PE
        restored_file = Path(f"/tmp/verify_{sample_name}.exe")
        
        try:
            result = subprocess.run([
                sys.executable, 
                str(utils_dir / "pe_to_image.py"),
                str(png_file),
                str(restored_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ {sample_name}: PNG to PE conversion failed")
                print(f"   Error: {result.stderr.strip()}")
                all_passed = False
                continue
            
            # Calculate hashes
            original_hash = calculate_sha256(original_file)
            restored_hash = calculate_sha256(restored_file)
            
            if original_hash == restored_hash:
                print(f"✅ {sample_name}: Hash match ({original_hash[:16]}...)")
            else:
                print(f"❌ {sample_name}: Hash mismatch!")
                print(f"   Original: {original_hash}")
                print(f"   Restored: {restored_hash}")
                all_passed = False
            
            # Clean up
            if restored_file.exists():
                restored_file.unlink()
                
        except Exception as e:
            print(f"❌ {sample_name}: Error during verification - {e}")
            all_passed = False
    
    print("=" * 80)
    if all_passed:
        print("🎉 All samples passed integrity verification!")
        return True
    else:
        print("💥 Some samples failed integrity verification!")
        return False

def verify_single_sample(sample_name):
    """Verify a single sample by name"""
    
    source_dir = Path("/home/mihir/Downloads/to_be_evaded_ds_unpacked")
    png_dir = Path("/home/mihir/Dropper/png_embedded_samples")
    utils_dir = Path("/home/mihir/Dropper/utils")
    
    original_file = source_dir / sample_name
    png_file = png_dir / f"{sample_name}.png"
    
    if not original_file.exists():
        print(f"❌ Original file not found: {original_file}")
        return False
        
    if not png_file.exists():
        print(f"❌ PNG file not found: {png_file}")
        return False
    
    print(f"🔍 Verifying sample: {sample_name}")
    
    # Convert PNG back to PE
    restored_file = Path(f"/tmp/verify_{sample_name}.exe")
    
    try:
        result = subprocess.run([
            sys.executable, 
            str(utils_dir / "pe_to_image.py"),
            str(png_file),
            str(restored_file)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ PNG to PE conversion failed: {result.stderr.strip()}")
            return False
        
        # Calculate and compare hashes
        original_hash = calculate_sha256(original_file)
        restored_hash = calculate_sha256(restored_file)
        
        print(f"Original hash: {original_hash}")
        print(f"Restored hash: {restored_hash}")
        
        if original_hash == restored_hash:
            print("✅ Hash verification PASSED - Files are identical!")
            success = True
        else:
            print("❌ Hash verification FAILED - Files differ!")
            success = False
        
        # Clean up
        if restored_file.exists():
            restored_file.unlink()
            
        return success
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def main():
    if len(sys.argv) == 1:
        # Verify all samples
        success = verify_png_conversion_integrity()
    elif len(sys.argv) == 2:
        # Verify single sample
        sample_name = sys.argv[1]
        success = verify_single_sample(sample_name)
    else:
        print("Usage:")
        print("  python3 verify_png_integrity.py           # Verify all samples")
        print("  python3 verify_png_integrity.py <sample>  # Verify specific sample")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()