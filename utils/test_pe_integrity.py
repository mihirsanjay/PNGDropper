#!/usr/bin/env python3
"""
Definitive test to verify PE functionality preservation through PNG conversion
Tests the complete pipeline: PE → PNG → PE and validates binary integrity
"""

import sys
import os
import tempfile
from pathlib import Path
import hashlib

# Add utils to path
sys.path.append('utils')
import pe_to_image

def test_pe_roundtrip(pe_file_path):
    """Test PE → PNG → PE conversion for exact binary preservation"""
    print(f"🧪 Testing roundtrip conversion: {pe_file_path}")
    
    # Read original PE
    with open(pe_file_path, 'rb') as f:
        original_pe_data = f.read()
    
    original_size = len(original_pe_data)
    original_hash = hashlib.sha256(original_pe_data).hexdigest()
    
    print(f"  📊 Original PE: {original_size:,} bytes")
    print(f"  🔐 Original SHA256: {original_hash[:16]}...")
    
    # Step 1: Convert PE to PNG
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
        png_path = tmp_png.name
    
    try:
        print(f"  🖼️  Converting PE → PNG...")
        pe_to_image.pe_to_png(pe_file_path, png_path)
        
        if not os.path.exists(png_path):
            print(f"  ❌ PNG conversion failed!")
            return False
            
        png_size = os.path.getsize(png_path)
        print(f"  ✅ PNG created: {png_size:,} bytes")
        
        # Step 2: Convert PNG back to PE using our method
        print(f"  🔄 Converting PNG → PE...")
        reconstructed_pe_data = png_to_pe_python(png_path)
        
        if not reconstructed_pe_data:
            print(f"  ❌ PNG → PE conversion failed!")
            return False
            
        # Step 3: Compare original vs reconstructed
        reconstructed_size = len(reconstructed_pe_data)
        reconstructed_hash = hashlib.sha256(reconstructed_pe_data).hexdigest()
        
        print(f"  📊 Reconstructed: {reconstructed_size:,} bytes")
        print(f"  🔐 Reconstructed SHA256: {reconstructed_hash[:16]}...")
        
        # Exact comparison
        if original_pe_data == reconstructed_pe_data:
            print(f"  ✅ PERFECT MATCH! Binary identical after roundtrip")
            return True
        else:
            print(f"  ❌ MISMATCH! Data corrupted during conversion")
            
            # Detailed analysis
            diff_count = sum(1 for i in range(min(len(original_pe_data), len(reconstructed_pe_data))) 
                           if original_pe_data[i] != reconstructed_pe_data[i])
            print(f"  📊 Byte differences: {diff_count:,}")
            print(f"  📊 Size difference: {reconstructed_size - original_size:+,} bytes")
            
            return False
            
    finally:
        # Cleanup
        if os.path.exists(png_path):
            os.unlink(png_path)

def png_to_pe_python(png_path):
    """Python implementation of PNG → PE conversion (mirrors C code)"""
    try:
        from PIL import Image
        import numpy as np
        
        # Load PNG as grayscale
        with Image.open(png_path) as img:
            if img.mode != 'L':
                img = img.convert('L')
            
            # Get pixel array
            pixels = np.array(img)
            width, height = img.size
            
            # Convert pixels back to bytes
            pe_data = pixels.flatten().tobytes()
            
            # Validate PE structure and find actual size
            if len(pe_data) >= 64:
                # Check DOS signature
                if pe_data[0] == 0x4D and pe_data[1] == 0x5A:  # "MZ"
                    # Find PE header offset
                    pe_offset = int.from_bytes(pe_data[60:64], 'little')
                    
                    if pe_offset < len(pe_data) - 4:
                        # Check PE signature
                        if pe_data[pe_offset:pe_offset+2] == b'PE':
                            # Get SizeOfImage from PE header (offset +80 from PE signature)
                            size_offset = pe_offset + 80
                            if size_offset + 4 < len(pe_data):
                                actual_size = int.from_bytes(pe_data[size_offset:size_offset+4], 'little')
                                if 0 < actual_size <= len(pe_data):
                                    return pe_data[:actual_size]
            
            # Fallback: return full data
            return pe_data
            
    except Exception as e:
        print(f"  ❌ PNG decoding error: {e}")
        return None

def main():
    """Run roundtrip tests on malware samples"""
    print("🔬 PE Functionality Preservation Verification")
    print("=" * 60)
    
    # Test on first 5 original samples
    samples_dir = Path("/home/mihir/Downloads/to_be_evaded_ds_unpacked")
    
    if not samples_dir.exists():
        print(f"❌ Samples directory not found: {samples_dir}")
        return
    
    # Test first 3 samples for verification
    test_samples = []
    for i in [1, 2, 3]:
        sample_path = samples_dir / str(i)
        if sample_path.exists():
            test_samples.append(sample_path)
    
    if not test_samples:
        print("❌ No test samples found!")
        return
    
    print(f"🎯 Testing {len(test_samples)} samples for binary preservation...")
    print()
    
    passed = 0
    failed = 0
    
    for i, sample_path in enumerate(test_samples, 1):
        print(f"[{i}/{len(test_samples)}] Testing sample: {sample_path.name}")
        
        if test_pe_roundtrip(sample_path):
            passed += 1
        else:
            failed += 1
        print()
    
    # Final results
    print("=" * 60)
    print(f"🎯 ROUNDTRIP TEST RESULTS")
    print("=" * 60)
    print(f"✅ PASSED: {passed}/{len(test_samples)} samples")
    print(f"❌ FAILED: {failed}/{len(test_samples)} samples")
    
    if passed == len(test_samples):
        print("🎉 ALL TESTS PASSED! Functionality is 100% preserved!")
        print("💡 Binary integrity confirmed - malware samples remain fully functional")
    else:
        print("⚠️  SOME TESTS FAILED! Pipeline may corrupt data")
        print("🔧 Investigation needed before using droppers")

if __name__ == "__main__":
    main()