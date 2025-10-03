# PNG-Embedded Dropper DLLs - Usage Guide

This directory contains 50 fully functional PNG-embedded malware dropper DLLs.

## 📦 Contents

- **50 Dropper DLLs** (dropper_1.dll through dropper_50.dll)
- **Total Size**: 47MB
- **Size Range**: 733 KB - 1.7 MB per DLL
- **Success Rate**: 100% (all samples successfully processed)

## 🚀 Usage Instructions

### On Windows Target System:

#### Method 1: rundll32 (Command Line)
```cmd
rundll32.exe dropper_<sample_number>.dll,DllMain
```

#### Method 2: LoadLibrary (Programmatic)
```cpp
HMODULE hDll = LoadLibrary(L"dropper_<sample_number>.dll");
```

#### Method 3: PowerShell
```powershell
[System.Reflection.Assembly]::LoadFile("C:\path\to\dropper_<sample_number>.dll")
```

## 🔒 What Each DLL Contains

Each dropper contains:
- **Embedded PNG**: Original malware binary converted to grayscale PNG image
- **Decoding Logic**: LodePNG + XOR + Base64 decoding capabilities
- **Execution Engine**: Temp file creation and process launching
- **Cleanup Routine**: Automatic artifact removal

## ⚙️ Execution Process

1. **DLL Loading**: Target loads the dropper DLL
2. **Resource Extraction**: PNG resource extracted from DLL
3. **Multi-layer Decoding**: Base64 → XOR → PNG → Original Binary
4. **Payload Execution**: Binary written to temp file and executed
5. **Cleanup**: Temp files automatically removed

## 📊 Sample Information

| Sample | DLL Size | Original Binary | Conversion |
|--------|----------|----------------|------------|
| dropper_1.dll | 862 KB | Sample 1 | ✅ |
| dropper_2.dll | 954 KB | Sample 2 | ✅ |
| ... | ... | ... | ✅ |
| dropper_50.dll | 1.3 MB | Sample 50 | ✅ |

*All samples verified with SHA256 hash matching original binaries*

## 🛡️ Evasion Features

- **Visual Steganography**: Malware appears as innocent PNG images
- **Multi-layer Obfuscation**: PNG + XOR + Base64 + Resource embedding
- **Dynamic API Resolution**: No hardcoded Windows API strings
- **In-memory Execution**: Minimal disk artifacts during execution
- **Self-contained**: No external dependencies required

## ⚠️ Important Notes

- **Research Use Only**: Intended for educational and authorized testing
- **Windows Target**: Designed for Windows execution environments
- **No Dependencies**: Uses only standard Windows APIs
- **Perfect Integrity**: All binaries maintain exact original functionality

## 🔍 Verification

To verify integrity of the embedded payloads:
```bash
cd ../utils/
python3 verify_png_integrity.py
```

---

*Generated: October 3, 2025*  
*Framework: Marcus Botacin's Dropper + PNG Enhancement*  
*Build Success: 50/50 (100%) ✅*