#!/usr/bin/env python3
"""
Comprehensive verification test for PNG dropper functionality preservation
Tests both conversion pipeline and PE structure integrity
"""

import sys
import os
import tempfile
import hashlib
import struct
from pathlib import Path

# Add utils to path
sys.path.append('utils')
import pe_to_image

def analyze_pe_structure(pe_data, label=""):
    """Analyze PE structure and extract key information"""
    print(f"📊 {label} PE Analysis:")
    
    if len(pe_data) < 64:
        print("  ❌ File too small to be valid PE")
        return None
        
    # DOS Header
    dos_sig = pe_data[:2]
    if dos_sig != b'MZ':
        print(f"  ❌ Invalid DOS signature: {dos_sig}")
        return None
    print(f"  ✅ DOS signature: {dos_sig}")
    
    # PE Header offset
    pe_offset = struct.unpack('<I', pe_data[60:64])[0]
    print(f"  📍 PE header offset: {pe_offset} (0x{pe_offset:x})")
    
    if pe_offset >= len(pe_data) - 4:
        print("  ❌ PE offset beyond file size")
        return None
        
    # PE Signature
    pe_sig = pe_data[pe_offset:pe_offset+4]
    if pe_sig != b'PE\x00\x00':
        print(f"  ❌ Invalid PE signature: {pe_sig}")
        return None
    print(f"  ✅ PE signature: {pe_sig}")
    
    # Machine type and characteristics
    machine = struct.unpack('<H', pe_data[pe_offset+4:pe_offset+6])[0]
    sections = struct.unpack('<H', pe_data[pe_offset+6:pe_offset+8])[0]
    print(f"  🏗️  Machine type: 0x{machine:x}, Sections: {sections}")
    
    # Optional header
    opt_header_size = struct.unpack('<H', pe_data[pe_offset+20:pe_offset+22])[0]
    if opt_header_size >= 24:
        magic = struct.unpack('<H', pe_data[pe_offset+24:pe_offset+26])[0]
        print(f"  🔮 Magic: 0x{magic:x} ({'PE32+' if magic == 0x20b else 'PE32' if magic == 0x10b else 'Unknown'})")
        
        # Entry point and image base
        if opt_header_size >= 40:
            entry_point = struct.unpack('<I', pe_data[pe_offset+40:pe_offset+44])[0]
            print(f"  🚀 Entry point: 0x{entry_point:x}")
            
        if opt_header_size >= 52:
            image_base = struct.unpack('<I', pe_data[pe_offset+52:pe_offset+56])[0] if magic == 0x10b else struct.unpack('<Q', pe_data[pe_offset+48:pe_offset+56])[0]
            print(f"  🏠 Image base: 0x{image_base:x}")
            
        if opt_header_size >= 56:
            size_of_image = struct.unpack('<I', pe_data[pe_offset+56:pe_offset+60])[0]
            print(f"  📏 SizeOfImage: {size_of_image:,} bytes")
            return size_of_image
    
    return None

def test_conversion_pipeline(pe_path, test_name):
    """Test complete PE → PNG → PE conversion pipeline"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {test_name}")
    print(f"📁 Source: {pe_path}")
    print(f"{'='*60}")
    
    # Step 1: Read original PE
    with open(pe_path, 'rb') as f:
        original_pe = f.read()
    
    original_size = len(original_pe)
    original_hash = hashlib.sha256(original_pe).hexdigest()
    
    print(f"📊 Original PE: {original_size:,} bytes")
    print(f"🔐 SHA256: {original_hash[:32]}...")
    
    # Analyze original PE structure
    original_sizeofimage = analyze_pe_structure(original_pe, "Original")
    
    # Step 2: Convert to PNG
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
        png_path = tmp_png.name
    
    try:
        print(f"\n🔄 Converting PE → PNG...")
        pe_to_image.pe_to_png(pe_path, png_path)
        
        if not os.path.exists(png_path):
            print("❌ PNG conversion failed!")
            return False
            
        png_size = os.path.getsize(png_path)
        print(f"✅ PNG created: {png_size:,} bytes")
        
        # Step 3: Convert PNG back to PE
        print(f"\n🔄 Converting PNG → PE...")
        
        # Method 1: Using metadata file (correct way)
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp_pe:
            restored_pe_path = tmp_pe.name
            
        restored_size = pe_to_image.png_to_pe(png_path, restored_pe_path)
        
        with open(restored_pe_path, 'rb') as f:
            restored_pe = f.read()
            
        restored_hash = hashlib.sha256(restored_pe).hexdigest()
        
        print(f"📊 Restored PE: {len(restored_pe):,} bytes")
        print(f"🔐 SHA256: {restored_hash[:32]}...")
        
        # Analyze restored PE structure  
        restored_sizeofimage = analyze_pe_structure(restored_pe, "Restored")
        
        # Step 4: Compare results
        print(f"\n📋 COMPARISON RESULTS:")
        print(f"{'Metric':<20} {'Original':<15} {'Restored':<15} {'Status':<10}")
        print(f"{'-'*65}")
        
        size_match = len(restored_pe) == original_size
        print(f"{'File Size':<20} {original_size:<15,} {len(restored_pe):<15,} {'✅' if size_match else '❌'}")
        
        hash_match = restored_hash == original_hash
        print(f"{'SHA256 Hash':<20} {'Match' if hash_match else 'Different':<15} {'':<15} {'✅' if hash_match else '❌'}")
        
        if original_sizeofimage and restored_sizeofimage:
            soi_match = original_sizeofimage == restored_sizeofimage
            print(f"{'SizeOfImage':<20} {original_sizeofimage:<15,} {restored_sizeofimage:<15,} {'✅' if soi_match else '❌'}")
        
        # Step 5: Byte-by-byte comparison if sizes match
        if size_match:
            print(f"\n🔍 Byte-by-byte comparison:")
            identical = original_pe == restored_pe
            print(f"  {'✅ PERFECT MATCH' if identical else '❌ BYTES DIFFER'}")
            
            if not identical:
                # Find first difference
                for i in range(min(len(original_pe), len(restored_pe))):
                    if original_pe[i] != restored_pe[i]:
                        print(f"  📍 First difference at byte {i}: {original_pe[i]} → {restored_pe[i]}")
                        break
        else:
            print(f"\n📏 Size difference: {len(restored_pe) - original_size:+,} bytes")
            
            if len(restored_pe) > original_size:
                # Check if extra bytes are padding
                extra_bytes = restored_pe[original_size:]
                if all(b == 0 for b in extra_bytes):
                    print(f"  ✅ Extra bytes are null padding (safe)")
                    # Test if trimmed version matches
                    trimmed_pe = restored_pe[:original_size]
                    if trimmed_pe == original_pe:
                        print(f"  ✅ Trimmed version matches original perfectly")
                        return True
                else:
                    print(f"  ❌ Extra bytes contain non-zero data")
        
        return hash_match and size_match
        
    finally:
        # Cleanup
        for path in [png_path, png_path + '.meta']:
            if os.path.exists(path):
                os.unlink(path)
        if 'restored_pe_path' in locals() and os.path.exists(restored_pe_path):
            os.unlink(restored_pe_path)

def main():
    """Run comprehensive verification tests"""
    print("🔬 PNG DROPPER FUNCTIONALITY VERIFICATION")
    print("=" * 80)
    
    # Test samples directory
    samples_dir = Path("/home/mihir/Downloads/to_be_evaded_ds_unpacked")
    
    if not samples_dir.exists():
        print(f"❌ Samples directory not found: {samples_dir}")
        return
    
    # Test first 5 samples for thorough verification
    test_samples = []
    for i in [1, 2, 3, 4, 5]:
        sample_path = samples_dir / str(i)
        if sample_path.exists():
            test_samples.append((sample_path, f"Sample {i}"))
    
    if not test_samples:
        print("❌ No test samples found!")
        return
    
    print(f"🎯 Testing {len(test_samples)} malware samples for conversion integrity...")
    
    passed = 0
    failed = 0
    
    for sample_path, test_name in test_samples:
        try:
            if test_conversion_pipeline(sample_path, test_name):
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"💥 {test_name}: ERROR - {e}")
        
        print()
    
    # Final results
    print("=" * 80)
    print(f"🎯 VERIFICATION RESULTS SUMMARY")
    print("=" * 80)
    print(f"✅ PASSED: {passed}/{len(test_samples)} samples")
    print(f"❌ FAILED: {failed}/{len(test_samples)} samples")
    print(f"📊 Success Rate: {(passed/len(test_samples)*100):.1f}%")
    
    if passed == len(test_samples):
        print("🎉 ALL TESTS PASSED! Conversion pipeline preserves PE functionality!")
        print("💡 Malware samples should retain full functionality after PNG conversion")
    elif passed > 0:
        print(f"⚠️  PARTIAL SUCCESS: {passed} samples passed, investigate {failed} failures")
    else:
        print("💥 ALL TESTS FAILED! Critical issues in conversion pipeline!")
        
    print("\n🔍 NEXT STEPS:")
    if failed > 0:
        print("  1. Investigate failed samples for conversion issues")
        print("  2. Check PE structure preservation")
        print("  3. Verify padding handling")
    else:
        print("  1. Test actual dropper execution on Windows")
        print("  2. Verify behavioral consistency")
        print("  3. Confirm evasion effectiveness")

if __name__ == "__main__":
    main()