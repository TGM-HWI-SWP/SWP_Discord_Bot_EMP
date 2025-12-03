@echo off
setlocal enabledelayedexpansion

:ask_mode
echo.
echo Choose startup mode:
echo 1. Full start (install dependencies and build)
echo 2. Quick restart (regenerate .env and restart Docker)
echo.
set /p mode="Enter choice (1 or 2): "

if "!mode!"=="1" goto full_start
if "!mode!"=="2" goto quick_restart
echo Invalid input. Please enter '1' or '2'.
goto ask_mode

:quick_restart
echo.
echo === Quick Restart Mode ===
echo.

if not defined VIRTUAL_ENV (
    if exist ".venv\Scripts\activate" (
        echo Activating virtual environment...
        call .venv\Scripts\activate
    ) else (
        echo Virtual environment not found. Please use Full start mode first.
        pause
        exit /b 1
    )
)

echo Generating .env from config.ini...
python src\discord_bot\init\config_loader.py

echo Restarting Docker services...
docker-compose restart

echo Initializing database data...
python src\discord_bot\init\db_loader.py

echo Quick restart complete!
pause
exit /b 0

:full_start
echo.
echo === Full Start Mode ===
echo.

if not exist ".venv" (
    echo Creating virtual environment...
    py -3.13 -m venv .venv
    echo Virtual environment created!
)

if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate
)

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

echo Generating .env from config.ini...
python src\discord_bot\init\config_loader.py

echo Starting Docker services...
docker-compose up -d --build

echo Initializing database data...
python src\discord_bot\init\db_loader.py

echo All services started!
pause
