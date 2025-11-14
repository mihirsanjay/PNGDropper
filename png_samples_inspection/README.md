# PNG Samples Inspection Folder

## Overview
This folder contains extracted PNG files from dropper DLLs for analysis and inspection purposes.

## Extracted Samples

| Sample | Dimensions | Size | Pixels | PE Detected |
|--------|------------|------|---------|-------------|
| dropper_1.png | 426 × 425 | 145.0 KB | 181,050 | ✅ MZ signature |
| dropper_10.png | 308 × 308 | 73.5 KB | 94,864 | ✅ MZ signature |
| dropper_11.png | 498 × 497 | 221.5 KB | 247,506 | ✅ MZ signature |
| dropper_12.png | 448 × 447 | 110.3 KB | 200,256 | ✅ MZ signature |
| dropper_13.png | 462 × 462 | 152.0 KB | 213,444 | ✅ MZ signature |

## Key Observations

### PNG Properties
- **Format**: 8-bit grayscale, non-interlaced PNG
- **Pixel values**: Full range 0-255 (confirms binary data encoding)
- **Mean values**: 100-127 (typical for executable code/data mix)
- **Dimensions**: Near-square (optimized for minimal file size)

### PE Validation
All extracted PNGs show correct PE signatures:
- **First two pixels**: 77, 90 (hex: 0x4D, 0x5A) = "MZ" DOS signature
- **Following bytes**: 144, 0, 3, 0... (typical DOS header continuation)

### Conversion Formula Verification
Each sample demonstrates the `width = ceil(sqrt(pe_size))` formula:
- Sample 10: 308² = 94,864 pixels (smallest sample)
- Sample 11: 498 × 497 = 247,506 pixels (largest sample)  
- Dimensions are near-square for optimal PNG compression

## Technical Analysis

### Binary-to-Pixel Mapping
```
PE Byte Value → PNG Pixel Grayscale Value
0x4D (77)  → Pixel value 77  ← DOS "M"
0x5A (90)  → Pixel value 90  ← DOS "Z" 
0x90 (144) → Pixel value 144 ← DOS header
0x00 (0)   → Pixel value 0   ← Padding/data
```

### Visual Appearance
These PNGs appear as grayscale "noise" or "static" when viewed as images because:
- Each pixel represents raw binary data (not visual content)
- PE executables contain mixed code/data with semi-random byte distribution
- No visual patterns - just executable machine code rendered as pixels

## Extraction Details
- **Source**: png_droppers_no_encoding/*.dll 
- **Method**: Resource extraction from IDR_PNG1 (ID 101, Type PNG)
- **Tool**: utils/extract_png_samples.py
- **Validation**: Automatic PE signature detection (MZ header verification)

## Usage
These extracted PNGs can be used for:
1. **Visual inspection** - See what PE-to-PNG conversion looks like
2. **Manual analysis** - Verify conversion quality and losslessness  
3. **Reverse testing** - Test PNG-to-PE reconstruction manually
4. **Research purposes** - Study binary data visualization techniques

## Security Note
⚠️ **These PNG files contain malware executables as pixel data**. While they are in PNG format, the pixel values represent actual malware code. Handle with appropriate security precautions.