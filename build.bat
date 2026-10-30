@echo off
REM ============================================================
REM  Build a standalone Windows exe for "A Slipery Climb".
REM  Requirements: Python 3.11+ on PATH, then run this file once.
REM ============================================================
cd /d "%~dp0"

echo [1/2] Installing build tools...
python -m pip install --upgrade pyinstaller || goto :error

echo [2/2] Building exe...
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
