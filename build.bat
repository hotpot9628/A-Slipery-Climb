@echo off
REM ============================================================
REM  Build a standalone Windows exe for "A SLIPERY CLIMB".
REM  Requirements: Python 3.11+ on PATH (pygame / PyInstaller
REM  are installed automatically). Just double-click this file.
REM ============================================================
cd /d "%~dp0"

REM The voice clips ship as one archive to keep the repo small:
REM unpack them once before PyInstaller packages sounds\.
if not exist "sounds\voice\en\line_00.mp3" (
  if exist "voice.zip" (
    echo [1/3] Unpacking voice clips...
    powershell -NoProfile -Command "Expand-Archive -Path 'voice.zip' -DestinationPath 'sounds' -Force" || goto :error
  ) else (
    echo [WARN] sounds\voice and voice.zip are both missing - the build will be silent.
  )
)

echo [2/3] Installing build tools...
python -m pip install --upgrade "pyinstaller>=6.0" pygame || goto :error

echo [3/3] Building exe...
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "A Slipery Climb" ^
  --icon icon.ico ^
  --add-data "textures;textures" ^
  --add-data "sounds;sounds" ^
  --add-data "fonts;fonts" ^
  --add-data "tutorial;tutorial" ^
  --version-file version_info.txt ^
  main.py || goto :error

echo.
echo Build finished:
echo   dist\A Slipery Climb.exe
pause
exit /b 0

:error
echo.
echo Build FAILED - see the messages above.
pause
exit /b 1
