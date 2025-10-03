@echo off
REM Build script for PNG-embedded droppers
REM Run this from Visual Studio Developer Command Prompt

set DROPPER_DIR=%~dp0png_embedded_samples

echo Building PNG-embedded droppers...

for /d %%d in ("%DROPPER_DIR%\dropper_*") do (
    echo Building %%~nd...
    pushd "%%d"
    
    REM Build using MSBuild
    msbuild Dropper.vcxproj /p:Configuration=Release /p:Platform=Win32
    
    if exist "Release\Dropper.dll" (
        echo ✓ Successfully built %%~nd
        copy "Release\Dropper.dll" "..\%%~nd.dll"
    ) else (
        echo ✗ Failed to build %%~nd
    )
    
    popd
)

echo Build process complete.
pause
