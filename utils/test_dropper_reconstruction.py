#!/usr/bin/env python3
"""
Test the actual dropper DLL PNG extraction and reconstruction
This simulates what happens at runtime in the dropper
"""

import sys
import os
import struct
import hashlib
from pathlib import Path

def extract_png_from_dropper(dll_path):
    """Extract PNG from dropper DLL (same as runtime)"""
    with open(dll_path, 'rb') as f:
        dll_data = f.read()
    
    # Find PNG signature (same logic as our extractor)
    png_signature = b'\x89PNG\r\n\x1a\n'
    png_start = -1
    
    start_pos = 0
    while True:
        pos = dll_data.find(png_signature, start_pos)
        if pos == -1:
            break
            
        # Check if followed by IHDR (real PNG)
        if dll_data[pos + 12:pos + 16] == b'IHDR':
            png_start = pos
            break
        start_pos = pos + 1
    
    if png_start == -1:
        return None
        
    # Find PNG end
    iend_pos = dll_data.find(b'IEND', png_start)
    if iend_pos == -1:
        return None
        
    png_end = iend_pos + 8
    png_data = dll_data[png_start:png_end]
    
    return png_data

def simulate_dropper_png_to_pe(png_data):
    """Simulate the C code png_to_pe() function"""
    try:
        from PIL import Image
        import numpy as np
        import io
        
        # Load PNG (simulates lodepng_decode_memory)
        img = Image.open(io.BytesIO(png_data))
        if img.mode != 'L':
            img = img.convert('L')
        
        width, height = img.size
        pixels = np.array(img)
        
        # Convert pixels to bytes (simulates memcpy from image_data)
        pe_data = pixels.flatten().tobytes()
        
        # Simulate PE validation and size detection
        if len(pe_data) >= 64:
            # Check DOS signature
            if pe_data[0] == 0x4D and pe_data[1] == 0x5A:  # "MZ"
                # Find PE header
                pe_offset = struct.unpack('<I', pe_data[60:64])[0]
                
                if pe_offset < len(pe_data) - 4:
                    # Check PE signature  
                    if pe_data[pe_offset:pe_offset+2] == b'PE':
                        # This is where our C code might be wrong!
                        # It uses SizeOfImage, but let's see what happens
                        
                        # Option 1: Use full image data (current C code path)
                        return pe_data
                        
                        # Option 2: Would need .meta file for correct size
                        # But dropper doesn't have access to .meta files!
        
        return pe_data
        
    except Exception as e:
        print(f"PNG decoding error: {e}")
        return None

def test_dropper_reconstruction(sample_num):
    """Test what our dropper actually reconstructs vs original"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING DROPPER RECONSTRUCTION: Sample {sample_num}")
    print(f"{'='*80}")
    
    # Paths
    original_path = Path(f"/home/mihir/Downloads/to_be_evaded_ds_unpacked/{sample_num}")
    dropper_path = Path(f"png_droppers_no_encoding/dropper_{sample_num}.dll")
    
    if not original_path.exists():
        print(f"❌ Original sample not found: {original_path}")
        return False
        
    if not dropper_path.exists():
        print(f"❌ Dropper DLL not found: {dropper_path}")
        return False
    
    # Read original sample
    with open(original_path, 'rb') as f:
        original_pe = f.read()
    
    original_size = len(original_pe)
    original_hash = hashlib.sha256(original_pe).hexdigest()
    
    print(f"📊 Original PE: {original_size:,} bytes")
    print(f"🔐 Original SHA256: {original_hash[:32]}...")
    
    # Extract PNG from dropper (runtime simulation)
    print(f"\n🔄 Extracting PNG from dropper DLL...")
    png_data = extract_png_from_dropper(dropper_path)
    
    if not png_data:
        print(f"❌ Failed to extract PNG from dropper")
        return False
        
    print(f"✅ PNG extracted: {len(png_data):,} bytes")
    
    # Simulate dropper reconstruction
    print(f"\n🔄 Simulating dropper PNG→PE reconstruction...")
    reconstructed_pe = simulate_dropper_png_to_pe(png_data)
    
    if not reconstructed_pe:
        print(f"❌ Failed to reconstruct PE from PNG")
        return False
        
    reconstructed_size = len(reconstructed_pe)
    reconstructed_hash = hashlib.sha256(reconstructed_pe).hexdigest()
    
    print(f"📊 Reconstructed PE: {reconstructed_size:,} bytes")
    print(f"🔐 Reconstructed SHA256: {reconstructed_hash[:32]}...")
    
    # Compare results
    print(f"\n📋 DROPPER RECONSTRUCTION COMPARISON:")
    print(f"{'Metric':<20} {'Original':<20} {'Dropper Output':<20} {'Status'}")
    print(f"{'-'*80}")
    
    size_match = reconstructed_size == original_size
    hash_match = reconstructed_hash == original_hash
    
    print(f"{'File Size':<20} {original_size:<20,} {reconstructed_size:<20,} {'✅' if size_match else '❌'}")
    print(f"{'SHA256 Hash':<20} {'Match' if hash_match else 'Different':<20} {'':<20} {'✅' if hash_match else '❌'}")
    
    if not size_match:
        size_diff = reconstructed_size - original_size
        print(f"{'Size Difference':<20} {'':<20} {size_diff:+,} bytes")
        
        if size_diff > 0:
            # Check if extra is padding
            if reconstructed_size > original_size:
                trimmed = reconstructed_pe[:original_size]
                if trimmed == original_pe:
                    print(f"{'Trimmed Match':<20} {'N/A':<20} {'✅ Perfect':<20} {'✅'}")
                    print(f"\n💡 ANALYSIS: Dropper adds {size_diff} padding bytes but core PE is identical")
                    return True
    
    if hash_match and size_match:
        print(f"\n🎉 PERFECT MATCH: Dropper reconstructs identical binary!")
        return True
    elif not hash_match:
        print(f"\n❌ HASH MISMATCH: Dropper corrupts the binary during reconstruction!")
        return False
    
    return False

def main():
    """Test dropper reconstruction vs original samples"""
    print("🔬 DROPPER RECONSTRUCTION VERIFICATION")
    print("Testing what our dropper DLLs actually reconstruct at runtime")
    print("=" * 80)
    
    # Test first 3 samples
    samples_to_test = [1, 2, 3]
    
    passed = 0
    failed = 0
    
    for sample_num in samples_to_test:
        try:
            if test_dropper_reconstruction(sample_num):
                passed += 1
                print(f"✅ Sample {sample_num}: DROPPER RECONSTRUCTION SUCCESSFUL")
            else:
                failed += 1
                print(f"❌ Sample {sample_num}: DROPPER RECONSTRUCTION FAILED")
        except Exception as e:
            failed += 1
            print(f"💥 Sample {sample_num}: ERROR - {e}")
    
    # Final results
    print(f"\n{'='*80}")
    print(f"🎯 DROPPER RECONSTRUCTION RESULTS")
    print(f"{'='*80}")
    print(f"✅ SUCCESSFUL: {passed}/{len(samples_to_test)} samples")
    print(f"❌ FAILED: {failed}/{len(samples_to_test)} samples")
    
    if passed == len(samples_to_test):
        print(f"🎉 ALL DROPPER TESTS PASSED!")
        print(f"💡 Our dropper DLLs correctly reconstruct original malware")
    else:
        print(f"⚠️  DROPPER ISSUES DETECTED!")
        print(f"🔧 The C code in Source.cpp may have reconstruction problems")

if __name__ == "__main__":
    main()