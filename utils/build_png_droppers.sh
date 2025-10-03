#!/bin/bash
#
# Build script for PNG-embedded dropper DLLs
# Cross-compiles Windows DLLs on Linux using MinGW
#

set -e  # Exit on any error

# Configuration
DROPPER_DIR="/home/mihir/Dropper/png_embedded_samples"
BUILD_LOG="build_log.txt"
CROSS_COMPILER="x86_64-w64-mingw32-g++"
WINDRES="x86_64-w64-mingw32-windres"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔨 Building PNG-embedded dropper DLLs...${NC}"
echo "Cross-compiler: $CROSS_COMPILER"
echo "Resource compiler: $WINDRES"
echo "Output directory: $DROPPER_DIR"
echo "Build log: $BUILD_LOG"
echo "=============================================="

# Clear previous build log
> "$BUILD_LOG"

# Check if cross-compiler exists
if ! command -v $CROSS_COMPILER &> /dev/null; then
    echo -e "${RED}❌ Cross-compiler not found: $CROSS_COMPILER${NC}"
    echo "Install with: sudo apt install mingw-w64"
    exit 1
fi

# Build function
build_dropper() {
    local sample_name=$1
    local dropper_path="${DROPPER_DIR}/dropper_${sample_name}"
    
    echo -e "\n${YELLOW}Building dropper for sample: $sample_name${NC}"
    
    if [ ! -d "$dropper_path" ]; then
        echo -e "${RED}❌ Dropper directory not found: $dropper_path${NC}"
        return 1
    fi
    
    cd "$dropper_path"
    
    # Check required files
    local required_files=("Source_Simple.cpp" "lodepng.cpp" "lodepng.h" "resource.h" "Resource.rc" "payload.png")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo -e "${RED}❌ Missing required file: $file${NC}"
            return 1
        fi
    done
    
    echo "  📁 Files present: ✓"
    
    # Compile resource file
    echo "  🔧 Compiling resources..."
    if ! $WINDRES Resource.rc -O coff -o Resource.res >> "$BUILD_LOG" 2>&1; then
        echo -e "${RED}❌ Resource compilation failed${NC}"
        tail -n 10 "$BUILD_LOG"
        return 1
    fi
    
    # Compile DLL
    echo "  🔧 Compiling DLL..."
    local compile_flags=(
        -shared
        -o "dropper_${sample_name}.dll"
        Source_Simple.cpp
        lodepng.cpp
        Resource.res
        -luser32
        -lkernel32
        -ladvapi32
        -lshell32
        -static-libgcc
        -static-libstdc++
        -Wl,--subsystem,windows
    )
    
    if ! $CROSS_COMPILER "${compile_flags[@]}" >> "$BUILD_LOG" 2>&1; then
        echo -e "${RED}❌ DLL compilation failed${NC}"
        echo "Last 20 lines of build log:"
        tail -n 20 "$BUILD_LOG"
        return 1
    fi
    
    # Verify output
    if [ -f "dropper_${sample_name}.dll" ]; then
        local dll_size=$(stat -c%s "dropper_${sample_name}.dll")
        echo -e "${GREEN}  ✅ Success! DLL size: ${dll_size} bytes${NC}"
        
        # Copy to main samples directory
        cp "dropper_${sample_name}.dll" "$DROPPER_DIR/"
        echo "  📦 Copied to: $DROPPER_DIR/dropper_${sample_name}.dll"
        return 0
    else
        echo -e "${RED}❌ DLL file not created${NC}"
        return 1
    fi
}

# Find all dropper directories
dropper_dirs=($(find "$DROPPER_DIR" -maxdepth 1 -name "dropper_*" -type d | sort))

if [ ${#dropper_dirs[@]} -eq 0 ]; then
    echo -e "${RED}❌ No dropper directories found in $DROPPER_DIR${NC}"
    exit 1
fi

echo -e "${YELLOW}Found ${#dropper_dirs[@]} dropper directories to build${NC}"

# Build statistics
successful_builds=0
failed_builds=0
build_start_time=$(date +%s)

# Build each dropper
for dropper_dir in "${dropper_dirs[@]}"; do
    sample_name=$(basename "$dropper_dir" | sed 's/dropper_//')
    
    if build_dropper "$sample_name"; then
        ((successful_builds++))
    else
        ((failed_builds++))
        echo -e "${RED}Failed to build dropper for sample: $sample_name${NC}"
    fi
done

# Build summary
build_end_time=$(date +%s)
build_duration=$((build_end_time - build_start_time))

echo ""
echo "=============================================="
echo -e "${YELLOW}📊 Build Summary${NC}"
echo "  Total droppers: $((successful_builds + failed_builds))"
echo -e "  ${GREEN}Successful: $successful_builds${NC}"
echo -e "  ${RED}Failed: $failed_builds${NC}"
echo "  Build time: ${build_duration} seconds"

if [ $successful_builds -gt 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Built DLL files:${NC}"
    ls -la "$DROPPER_DIR"/*.dll 2>/dev/null || echo "  No DLL files found in output directory"
fi

if [ $failed_builds -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Check build log for details: $BUILD_LOG${NC}"
fi

echo ""
if [ $successful_builds -gt 0 ]; then
    echo -e "${GREEN}🎉 Build completed! You can now test the dropper DLLs.${NC}"
    echo ""
    echo "To test a dropper DLL:"
    echo "  1. Copy the DLL to a Windows machine"  
    echo "  2. Use: rundll32.exe dropper_<sample>.dll,DllMain"
    echo "  3. Or load it programmatically with LoadLibrary()"
else
    echo -e "${RED}💥 All builds failed. Check the build log and file permissions.${NC}"
fi