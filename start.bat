@echo off
setlocal enabledelayedexpansion

echo Checking for virtual environment...
if defined VIRTUAL_ENV (
    echo Already in an activated virtual environment!
) else if not exist ".venv" (
    echo Creating virtual environment...
    python -3.13 -m venv .venv
    echo Virtual environment created!
    
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    
    :ask_dev
    set /p install_dev="Do you want to install dev dependencies? (y/n): "
    
    if /i "!install_dev!"=="y" (
        echo Installing dependencies with dev extras from pyproject.toml...
        pip install -e .[dev]
        echo Dependencies installed!
    ) else if /i "!install_dev!"=="n" (
        echo Installing dependencies from pyproject.toml...
        pip install -e .
        echo Dependencies installed!
    ) else (
        echo Invalid input. Please enter 'y' or 'n'.
        goto ask_dev
    )
) else (
    echo Virtual environment already exists!
    call .venv\Scripts\activate.bat
)

echo Generating .env from config.ini...
python src\discord_bot\init\config_loader.py

echo Starting Docker services...
docker-compose up -d

echo Uploading initial database data...
python src\discord_bot\init\db_loader.py

echo All services started!
pause
