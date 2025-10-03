# Dropper - Advanced Malware Delivery Framework

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
*Build Success Rate: 100% 🎯*