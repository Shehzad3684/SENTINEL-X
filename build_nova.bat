@echo off
:: ============================================================
:: Nova AI Auto-Builder Script
:: Builds a standalone .exe with all dependencies
:: ============================================================

echo.
echo ========================================
echo    NOVA AI - AUTO BUILD SCRIPT
echo ========================================
echo.

:: Step 1: Install Dependencies
echo [1/4] Installing Python Dependencies...
pip install pyautogui pygetwindow psutil pygame SpeechRecognition edge-tts groq pyperclip pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo      Done!

:: Step 2: Build the EXE
echo.
echo [2/4] Building Nova_AI.exe with PyInstaller...
pyinstaller --noconsole --onefile --name "Nova_AI" --icon=assets/icon.ico --add-data "assets;assets" app/gui.py 2>nul
if not exist "dist\Nova_AI.exe" (
    :: Try without icon if it doesn't exist
    pyinstaller --noconsole --onefile --name "Nova_AI" --add-data "assets;assets" app/gui.py
)
if errorlevel 1 (
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)
echo      Done!

:: Step 3: Create Release Folder
echo.
echo [3/4] Creating Nova_Release folder...
if exist "Nova_Release" rmdir /s /q "Nova_Release"
mkdir "Nova_Release"

:: Move EXE
move "dist\Nova_AI.exe" "Nova_Release\" >nul

:: Create README
echo NOVA AI - Voice-Controlled Desktop Automation > "Nova_Release\README.txt"
echo ============================================= >> "Nova_Release\README.txt"
echo. >> "Nova_Release\README.txt"
echo HOW TO USE: >> "Nova_Release\README.txt"
echo 1. Double-click Nova_AI.exe to launch >> "Nova_Release\README.txt"
echo 2. Click "Start Listening" to enable voice commands >> "Nova_Release\README.txt"
echo 3. Speak commands like: >> "Nova_Release\README.txt"
echo    - "Open Chrome" >> "Nova_Release\README.txt"
echo    - "Play Despacito on YouTube" >> "Nova_Release\README.txt"
echo    - "Write an essay about Artificial Intelligence" >> "Nova_Release\README.txt"
echo    - "Open WhatsApp" >> "Nova_Release\README.txt"
echo    - "Take a screenshot" >> "Nova_Release\README.txt"
echo    - "Status report" >> "Nova_Release\README.txt"
echo. >> "Nova_Release\README.txt"
echo REQUIREMENTS: >> "Nova_Release\README.txt"
echo - Windows 10/11 >> "Nova_Release\README.txt"
echo - Microphone for voice commands >> "Nova_Release\README.txt"
echo - Internet connection for AI features >> "Nova_Release\README.txt"
echo. >> "Nova_Release\README.txt"
echo Built with Python, PyAutoGUI, and Groq AI >> "Nova_Release\README.txt"

echo      Done!

:: Step 4: Cleanup
echo.
echo [4/4] Cleaning up build files...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Nova_AI.spec" del "Nova_AI.spec"
echo      Done!

:: Complete
echo.
echo ========================================
echo    BUILD COMPLETE!
echo ========================================
echo.
echo Your executable is ready at:
echo    Nova_Release\Nova_AI.exe
echo.
echo Press any key to open the release folder...
pause >nul
explorer "Nova_Release"
