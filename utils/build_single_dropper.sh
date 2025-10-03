#!/bin/bash
#
# Build script for single PNG-embedded dropper DLL
# Called by the batch processor
#

# Arguments
SAMPLE_NAME="$1"
BUILD_DIR="$2" 
OUTPUT_DIR="$3"

# Configuration
CROSS_COMPILER="x86_64-w64-mingw32-g++"
WINDRES="x86_64-w64-mingw32-windres"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

if [ $# -ne 3 ]; then
    echo -e "${RED}Usage: $0 <sample_name> <build_dir> <output_dir>${NC}"
    exit 1
fi

# Enter build directory
cd "$BUILD_DIR" || exit 1

# Check required files exist
required_files=("Source_Simple.cpp" "lodepng.cpp" "lodepng.h" "resource.h" "Resource.rc" "payload.png")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}Missing required file: $file${NC}" >&2
        exit 1
    fi
done

# Compile resource file
if ! $WINDRES Resource.rc -O coff -o Resource.res >/dev/null 2>&1; then
    echo -e "${RED}Resource compilation failed${NC}" >&2
    exit 1
fi

# Compile DLL
compile_flags=(
    -shared
    -o "dropper_${SAMPLE_NAME}.dll"
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

if ! $CROSS_COMPILER "${compile_flags[@]}" >/dev/null 2>&1; then
    echo -e "${RED}DLL compilation failed${NC}" >&2
    exit 1
fi

# Verify and move output
if [ -f "dropper_${SAMPLE_NAME}.dll" ]; then
    mv "dropper_${SAMPLE_NAME}.dll" "$OUTPUT_DIR/"
    exit 0
else
    echo -e "${RED}DLL file not created${NC}" >&2
    exit 1
fi