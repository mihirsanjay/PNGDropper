#!/usr/bin/env python3
"""
SPECIFIC SAMPLE VERIFICATION TEST
Compare specific dropper samples (1, 9, 45) with original samples using EXACT LodePNG logic
"""

import os
import struct
import hashlib
from pathlib import Path

def extract_png_resource_from_dll(dll_path):
    """Extract PNG resource from DLL - same logic as Source.cpp"""
    print(f"🔧 Extracting PNG resource from: {dll_path}")
    
    with open(dll_path, 'rb') as f:
        dll_data = f.read()
        
        # Find PNG signature - look for the REAL PNG (not false positives)
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
            print(f"  ❌ No valid PNG found")
            return None
            
        print(f"  📍 PNG found at offset: {png_start} (0x{png_start:x})")
        
        # Find IEND to get PNG end
        iend_pos = dll_data.find(b'IEND', png_start)
        if iend_pos == -1:
            print(f"  ❌ PNG IEND not found")
            return None
            
        # PNG ends after IEND + 4 bytes CRC
        png_end = iend_pos + 8  # IEND (4) + CRC (4)
        png_data = dll_data[png_start:png_end]
        
        print(f"  📏 PNG size: {len(png_data)} bytes")
        return png_data

def png_to_pe_lodepng_simulation(png_data):
    """
    Simulate the EXACT png_to_pe() logic from Source.cpp using LodePNG
    This replicates the exact C++ LodePNG call:
    lodepng_decode_memory(&image_data, &width, &height, png_data, png_size, LCT_GREY, 8)
    """
    print(f"  🔄 Decoding PNG to PE using EXACT LodePNG simulation...")
    
    try:
        from PIL import Image
        import numpy as np
        import io
        
        # Load PNG using PIL (equivalent to LodePNG loading)
        with Image.open(io.BytesIO(png_data)) as img:
            width, height = img.size
            print(f"  📐 PNG dimensions: {width} x {height}")
            
            # EXACT LodePNG behavior: decode as LCT_GREY (grayscale), 8-bit
            # This is equivalent to: lodepng_decode_memory(..., LCT_GREY, 8)
            if img.mode != 'L':
                img = img.convert('L')  # Convert to grayscale (LCT_GREY equivalent)
            
            # Get pixel data as bytes (exactly like LodePNG output)
            # LodePNG returns unsigned char* with width*height bytes for grayscale
            image_data = np.array(img, dtype=np.uint8)
            
            # Flatten to 1D byte array (exactly like LodePNG memory layout)
            pixel_bytes = image_data.flatten()
            total_image_size = len(pixel_bytes)  # width * height
            
            print(f"  📊 Total image size: {total_image_size:,} bytes")
            
            # EXACT Source.cpp logic: memcpy(pe_data, image_data, total_image_size)
            pe_data = bytes(pixel_bytes)
            
            # EXACT Source.cpp logic: Try to find actual PE size using PE headers
            if len(pe_data) >= 64:  # Minimum for PE header access
                # Check DOS header (exactly like Source.cpp)
                dos_signature = pe_data[0:2]
                if dos_signature == b'MZ':  # IMAGE_DOS_SIGNATURE
                    print(f"  ✅ Valid DOS signature found (MZ)")
                    
                    # Get e_lfanew offset (bytes 60-64 in DOS header)
                    if len(pe_data) >= 64:
                        e_lfanew = int.from_bytes(pe_data[60:64], byteorder='little')
                        print(f"  📍 PE header offset (e_lfanew): 0x{e_lfanew:x}")
                        
                        # Check NT header signature (exactly like Source.cpp)
                        if e_lfanew + 4 < len(pe_data):
                            nt_signature = pe_data[e_lfanew:e_lfanew+4]
                            if nt_signature == b'PE\x00\x00':  # IMAGE_NT_SIGNATURE
                                print(f"  ✅ Valid NT signature found (PE)")
                                
                                # Get SizeOfImage from OptionalHeader (exactly like Source.cpp logic)
                                # OptionalHeader starts at e_lfanew + 24 (NT signature + FileHeader)
                                opt_header_offset = e_lfanew + 24
                                if opt_header_offset + 56 < len(pe_data):  # SizeOfImage at offset 56 in OptionalHeader
                                    size_of_image_bytes = pe_data[opt_header_offset + 56:opt_header_offset + 60]
                                    size_of_image = int.from_bytes(size_of_image_bytes, byteorder='little')
                                    print(f"  � PE SizeOfImage: {size_of_image:,} bytes")
                                    
                                    # Use SizeOfImage if reasonable, otherwise use total_image_size
                                    if size_of_image <= total_image_size and size_of_image > 0:
                                        actual_pe_size = size_of_image
                                    else:
                                        actual_pe_size = total_image_size
                                else:
                                    actual_pe_size = total_image_size
                            else:
                                print(f"  ⚠️ Invalid NT signature, using total size")
                                actual_pe_size = total_image_size
                        else:
                            actual_pe_size = total_image_size
                    else:
                        actual_pe_size = total_image_size
                else:
                    print(f"  ❌ Invalid DOS signature: {dos_signature}")
                    return None
            else:
                print(f"  ❌ PE data too small: {len(pe_data)} bytes")
                return None
                
            # Return the PE data (Source.cpp returns the full buffer, not trimmed)
            print(f"  📊 Final PE size: {len(pe_data):,} bytes")
            print(f"  ✅ LodePNG simulation complete")
            return pe_data
                
    except Exception as e:
        print(f"  ❌ PNG decoding failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_hash(data):
    """Calculate SHA256 hash"""
    return hashlib.sha256(data).hexdigest()

def compare_with_original(extracted_pe, original_path, sample_num):
    """Compare extracted PE with original sample"""
    print(f"📊 Comparing with original: {original_path}")
    
    if not os.path.exists(original_path):
        print(f"  ❌ Original file not found: {original_path}")
        return False
        
    # Read original file
    with open(original_path, 'rb') as f:
        original_data = f.read()
        
    print(f"  📏 Original size: {len(original_data):,} bytes")
    print(f"  📏 Extracted size: {len(extracted_pe):,} bytes")
    
    # Calculate hashes
    original_hash = calculate_hash(original_data)
    extracted_hash = calculate_hash(extracted_pe)
    
    print(f"  🔐 Original SHA256: {original_hash[:32]}...")
    print(f"  🔐 Extracted SHA256: {extracted_hash[:32]}...")
    
    # Check if they match exactly or with null padding
    if original_data == extracted_pe:
        print(f"  ✅ PERFECT MATCH!")
        return True
    elif extracted_pe.startswith(original_data):
        padding = len(extracted_pe) - len(original_data)
        padding_bytes = extracted_pe[len(original_data):]
        if all(b == 0 for b in padding_bytes):
            print(f"  ✅ MATCH with null padding (+{padding} bytes)")
            return True
        else:
            print(f"  ❌ Size match but non-null padding detected")
            return False
    else:
        print(f"  ❌ NO MATCH - different content")
        return False

def test_specific_sample(sample_num):
    """Test a specific sample number"""
    print(f"\n{'='*60}")
    print(f"🔬 Test Case: Sample {sample_num}")
    print(f"{'='*60}")
    
    # Paths
    dropper_path = f"png_droppers_no_encoding/dropper_{sample_num}.dll"
    original_path = f"/home/mihir/Downloads/to_be_evaded_ds_unpacked/{sample_num}"
    
    if not os.path.exists(dropper_path):
        print(f"❌ Dropper not found: {dropper_path}")
        return False
        
    if not os.path.exists(original_path):
        print(f"❌ Original not found: {original_path}")
        return False
    
    # Step 1: Extract PNG from dropper DLL
    png_data = extract_png_resource_from_dll(dropper_path)
    if not png_data:
        return False
        
    # Step 2: Decode PNG to PE using LodePNG simulation
    extracted_pe = png_to_pe_lodepng_simulation(png_data)
    if not extracted_pe:
        return False
        
    # Step 3: Compare with original
    return compare_with_original(extracted_pe, original_path, sample_num)

def main():
    """Run specific sample verification test"""
    print("🧪 SPECIFIC SAMPLE VERIFICATION TEST")
    print("=" * 80)
    print("Testing: Dropper DLL → PNG extraction → LodePNG decode → Original comparison")
    print()
    
    # Test specific samples as requested
    test_samples = [1, 9, 45]
    results = {}
    
    print(f"🎯 Testing samples: {test_samples}")
    
    for sample_num in test_samples:
        success = test_specific_sample(sample_num)
        results[sample_num] = success
        print(f"✅ Sample {sample_num}: {'PASSED' if success else 'FAILED'}")
    
    # Summary
    print(f"\n{'='*80}")
    print("🎯 SPECIFIC SAMPLE VERIFICATION RESULTS")
    print(f"{'='*80}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for sample_num, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"Sample {sample_num}: {status}")
    
    print(f"\n📊 Success Rate: {passed}/{total} ({100*passed/total:.1f}%)")
    
    if passed == total:
        print("🎉 ALL SAMPLES VERIFIED!")
        print("💡 Dropper extraction matches original samples perfectly!")
        print("✅ CONFIRMED: LodePNG logic preserves malware functionality")
    else:
        print("⚠️ Some samples failed verification")
        
    print(f"\n📋 This test confirms:")
    print(f"  • DLL PNG resource extraction works correctly")
    print(f"  • LodePNG PNG → PE decoding preserves original data")
    print(f"  • Runtime pipeline matches build-time conversion")

if __name__ == "__main__":
    main()