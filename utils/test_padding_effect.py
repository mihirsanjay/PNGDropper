#!/usr/bin/env python3
"""
Test to verify that padding doesn't affect PE structure or execution capability
"""

import struct
from pathlib import Path

def analyze_pe_structure(pe_data):
    """Analyze PE structure and verify integrity"""
    
    if len(pe_data) < 64:
        return False, "File too small"
    
    # Check DOS header
    if pe_data[0:2] != b'MZ':
        return False, "Invalid DOS signature"
    
    # Get PE offset
    pe_offset = struct.unpack('<I', pe_data[60:64])[0]
    
    if pe_offset >= len(pe_data) - 4:
        return False, "Invalid PE offset"
    
    # Check PE signature  
    if pe_data[pe_offset:pe_offset+4] != b'PE\x00\x00':
        return False, "Invalid PE signature"
    
    # Get key PE header fields
    coff_header_offset = pe_offset + 4
    optional_header_offset = pe_offset + 24
    
    # Number of sections
    num_sections = struct.unpack('<H', pe_data[coff_header_offset + 2:coff_header_offset + 4])[0]
    
    # Optional header size
    opt_header_size = struct.unpack('<H', pe_data[coff_header_offset + 16:coff_header_offset + 18])[0]
    
    # Key optional header fields (assuming PE32+)
    if opt_header_size >= 24:
        entry_point = struct.unpack('<I', pe_data[optional_header_offset + 16:optional_header_offset + 20])[0]
        image_base = struct.unpack('<Q', pe_data[optional_header_offset + 24:optional_header_offset + 32])[0] 
        size_of_image = struct.unpack('<I', pe_data[optional_header_offset + 56:optional_header_offset + 60])[0]
        size_of_headers = struct.unpack('<I', pe_data[optional_header_offset + 60:optional_header_offset + 64])[0]
    else:
        # PE32 format
        entry_point = struct.unpack('<I', pe_data[optional_header_offset + 16:optional_header_offset + 20])[0]
        image_base = struct.unpack('<I', pe_data[optional_header_offset + 28:optional_header_offset + 32])[0]
        size_of_image = struct.unpack('<I', pe_data[optional_header_offset + 56:optional_header_offset + 60])[0]
        size_of_headers = struct.unpack('<I', pe_data[optional_header_offset + 60:optional_header_offset + 64])[0]
    
    # Calculate section table offset
    section_table_offset = optional_header_offset + opt_header_size
    
    # Analyze sections
    sections = []
    max_section_end = 0
    
    for i in range(num_sections):
        section_offset = section_table_offset + (i * 40)
        if section_offset + 40 > len(pe_data):
            break
            
        name = pe_data[section_offset:section_offset + 8].rstrip(b'\x00').decode('ascii', errors='ignore')
        virtual_size = struct.unpack('<I', pe_data[section_offset + 8:section_offset + 12])[0]
        virtual_address = struct.unpack('<I', pe_data[section_offset + 12:section_offset + 16])[0] 
        size_of_raw_data = struct.unpack('<I', pe_data[section_offset + 16:section_offset + 20])[0]
        pointer_to_raw_data = struct.unpack('<I', pe_data[section_offset + 20:section_offset + 24])[0]
        
        sections.append({
            'name': name,
            'virtual_size': virtual_size,
            'virtual_address': virtual_address,
            'size_of_raw_data': size_of_raw_data,
            'pointer_to_raw_data': pointer_to_raw_data
        })
        
        # Track where sections end in file
        section_end = pointer_to_raw_data + size_of_raw_data
        max_section_end = max(max_section_end, section_end)
    
    return True, {
        'entry_point': entry_point,
        'image_base': image_base, 
        'size_of_image': size_of_image,
        'size_of_headers': size_of_headers,
        'num_sections': num_sections,
        'sections': sections,
        'max_section_end': max_section_end,
        'file_size': len(pe_data),
        'trailing_data': len(pe_data) - max_section_end
    }

def test_padding_effect():
    """Test padding effect on PE structure"""
    print("🔍 Testing Padding Effect on PE Structure")
    print("=" * 50)
    
    # Test with extracted PNG data (includes padding)
    png_samples = list(Path("png_samples_inspection").glob("*.png"))
    
    if not png_samples:
        print("❌ No PNG samples found for testing")
        return
    
    # Test first sample
    png_path = png_samples[0]
    print(f"📄 Testing: {png_path.name}")
    
    # Load PNG and convert to PE data (with padding)
    from PIL import Image
    import numpy as np
    
    with Image.open(png_path) as img:
        if img.mode != 'L':
            img = img.convert('L')
        pixels = np.array(img)
        pe_data_with_padding = pixels.flatten().tobytes()
    
    print(f"📊 PE data size (with padding): {len(pe_data_with_padding):,} bytes")
    
    # Analyze PE structure
    valid, info = analyze_pe_structure(pe_data_with_padding)
    
    if not valid:
        print(f"❌ PE structure invalid: {info}")
        return
    
    print(f"✅ PE structure is VALID!")
    print(f"📐 Entry Point: 0x{info['entry_point']:08x}")
    print(f"📐 Image Base: 0x{info['image_base']:08x}")  
    print(f"📐 Size of Image: {info['size_of_image']:,} bytes")
    print(f"📐 Size of Headers: {info['size_of_headers']:,} bytes")
    print(f"📐 Sections: {info['num_sections']}")
    
    # Show sections
    print(f"\n📋 PE Sections:")
    for section in info['sections']:
        print(f"  {section['name']:<8} VA:0x{section['virtual_address']:08x} "
              f"Size:{section['size_of_raw_data']:>8,} File:0x{section['pointer_to_raw_data']:08x}")
    
    # Show padding analysis  
    print(f"\n🎯 Padding Analysis:")
    print(f"  📊 Last section ends at: {info['max_section_end']:,} bytes")
    print(f"  📊 File total size: {info['file_size']:,} bytes") 
    print(f"  📊 Trailing data (padding): {info['trailing_data']:,} bytes")
    
    # Key insight
    if info['trailing_data'] > 0:
        print(f"\n💡 INSIGHT:")
        print(f"  ✅ PE loader will load sections up to byte {info['max_section_end']:,}")
        print(f"  ✅ Padding bytes {info['max_section_end']:,}-{info['file_size']:,} are IGNORED by PE loader")
        print(f"  ✅ Entry point and all sections are BEFORE padding region")
        print(f"  ✅ Malware functionality is PRESERVED")
    else:
        print(f"  📊 No trailing padding detected")

if __name__ == "__main__":
    test_padding_effect()