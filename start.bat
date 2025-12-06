@echo off

if not exist "%~dp0\.venv\" (
    echo Creating virtual environment with Python 3.13...
    py -3.13 -m venv "%~dp0\.venv" 2>nul || python3.13 -m venv "%~dp0\.venv"
    echo Virtual environment created at "%~dp0\.venv"
) else (
    echo Virtual environment already exists, skipping creation
)

if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    if exist "%~dp0\.venv\Scripts\activate.bat" (
        call "%~dp0\.venv\Scripts\activate.bat"
        echo Virtual environment activated (cmd)
    ) else (
        echo Activation script not found for cmd. If you are running PowerShell, activate with:
        echo    PowerShell: .\"%~dp0\.venv\Scripts\Activate.ps1\"
        echo Or run this script from Command Prompt to have the venv activated in the same shell.
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
