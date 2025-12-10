@echo off

rem Parse optional action flags: -r/--restart, -o/--softstart
set ACTION=%1
if /i "%ACTION%"=="-r" set ACTION=restart
if /i "%ACTION%"=="--restart" set ACTION=restart
if /i "%ACTION%"=="-o" set ACTION=softstart
if /i "%ACTION%"=="--softstart" set ACTION=softstart

if not exist ".venv" (
    echo Creating virtual environment...
    py -3.13 -m venv .venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists, skipping creation!
)   

if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo Virtual environment activated!
) else (
    echo Virtual environment already activated, skipping activation!
)

echo Creating .env file and defining environment variables...
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

if /i "%ACTION%"=="restart" (
    echo Restarting containers...
    docker compose restart
) else if /i "%ACTION%"=="softstart" (
    echo Starting containers without rebuild...
    docker compose up -d
) else (
    echo Stopping and removing containers...
    docker compose down -v
    echo Building and starting containers...
    docker compose up --build -d
)

echo All services started!
pause
