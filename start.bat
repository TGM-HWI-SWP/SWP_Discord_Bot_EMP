@echo off

if not exist ".venv" (
    echo Creating virtual environment...
    py -3.13 -m venv .venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists, skipping creation!
)   

if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate
    echo Virtual environment activated!
) else (
    echo Virtual environment already activated, skipping activation!
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
echo Dependencies installed!

if "%1"=="restart" (
    docker compose restart
) else (
    docker compose up --build -d
)

echo All services started!
pause
