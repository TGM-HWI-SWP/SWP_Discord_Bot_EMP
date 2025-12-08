@echo off

REM Check if using Microsoft Store Python (creates Unix-style venvs)
for /f "tokens=*" %%i in ('where python 2^>nul') do (
    echo %%i | findstr /C:"WindowsApps" >nul
    if not errorlevel 1 (
        echo.
        echo ========================================
        echo ERROR: Microsoft Store Python detected!
        echo ========================================
        echo.
        echo Microsoft Store Python creates incompatible virtual environments.
        echo You MUST install Python 3.13 from python.org
        echo.
        echo 1. Download from: https://www.python.org/downloads/
        echo 2. Run the installer
        echo 3. CHECK "Add Python to PATH"
        echo 4. After installation, restart your terminal
        echo.
        pause
        exit /b 1
    )
)

if not exist "%~dp0\.venv\" (
    echo Creating virtual environment with Python 3.13...
    
    REM Try to create with py launcher first
    py -3.13 -m venv --copies "%~dp0\.venv" 2>nul
    
    REM If py doesn't exist or failed, try python3.13
    if not exist "%~dp0\.venv\Scripts\python.exe" (
        if not exist "%~dp0\.venv\bin\python.exe" (
            python3.13 -m venv --copies "%~dp0\.venv" 2>nul
        )
    )
    
    REM If still not created, try python
    if not exist "%~dp0\.venv\Scripts\python.exe" (
        if not exist "%~dp0\.venv\bin\python.exe" (
            python -m venv --copies "%~dp0\.venv" 2>nul
        )
    )
    
    REM Check result - prefer Scripts (Windows), but handle bin (Unix-style)
    if exist "%~dp0\.venv\Scripts\python.exe" (
        echo Virtual environment created successfully with Scripts folder
    ) else if exist "%~dp0\.venv\bin\python.exe" (
        echo Virtual environment created with Unix layout - copying to Scripts folder...
        xcopy /Y /E /I "%~dp0\.venv\bin" "%~dp0\.venv\Scripts" >nul
        if exist "%~dp0\.venv\Scripts\python.exe" (
            echo Successfully created Scripts folder
        ) else (
            echo ERROR: Could not create Scripts folder
            pause
            exit /b 1
        )
    ) else (
        echo ERROR: No Python installation found. Please install Python 3.13
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists
    REM Check if we need to create Scripts folder from bin
    if not exist "%~dp0\.venv\Scripts" (
        if exist "%~dp0\.venv\bin" (
            echo Fixing venv structure: copying bin to Scripts...
            xcopy /Y /E /I "%~dp0\.venv\bin" "%~dp0\.venv\Scripts" >nul
            if exist "%~dp0\.venv\Scripts\python.exe" (
                echo Scripts folder created successfully
            )
        )
    )
)

if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    if exist "%~dp0\.venv\Scripts\activate.bat" (
        call "%~dp0\.venv\Scripts\activate.bat"
        echo Virtual environment activated
    ) else (
        echo ERROR: Activation script not found at "%~dp0\.venv\Scripts\activate.bat"
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already activated, skipping activation
)

echo Creating environment variables...
python src\discord_bot\init\config_loader.py

for /f "tokens=2 delims==" %%a in ('findstr /i "^DEV_MODE=" .env') do set DEV_MODE=%%a

if /i "%DEV_MODE%"=="true" (
    echo Installing dependencies with dev extras...
    pip install -e .[dev]
) else (
    echo Installing dependencies...
    pip install -e .
)
echo Dependencies installed

if "%1"=="restart" (
    docker compose restart
) else (
    docker compose up --build -d
)

echo All services started
pause
