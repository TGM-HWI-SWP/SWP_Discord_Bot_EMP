# SWP Discord Bot

A Discord bot with a web interface, built using Clean Architecture principles. This school project demonstrates modern software engineering practices including hexagonal architecture, dependency inversion, and separation of concerns.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Docker Deployment](#docker-deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Fun Facts**: Fetch random fun facts from the database
- **Dish Suggestions**: Get meal recommendations based on categories (e.g., Italian, Asian)
- **Web Interface**: Manage and monitor your bot through a Gradio-powered web dashboard
- **Database Integration**: MongoDB-based persistent storage with Mongo Express web UI
- **Docker Support**: Full containerization with Docker Compose
- **Clean Architecture**: Fully decoupled components following hexagonal architecture principles
- **Translation Services** (Planned): Message translation capabilities

## Architecture

This project follows **Clean Architecture** (Hexagonal Architecture) principles, separating concerns into distinct layers:

```
┌─────────────────────────────────────────┐
│          Adapters (External)            │
│  ┌──────────────┬──────────────────┐    │
│  │  Database    │   View (Gradio)  │    │
│  │  (MongoDB)   │                  │    │
│  └──────────────┴──────────────────┘    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Business Logic (Core)           │
│  ┌────────────────────────────────────┐ │
│  │  • FunFactSelector                 │ │
│  │  • DishSelector                    │ │
│  │  • Translator (In Progress)        │ │
│  └────────────────────────────────────┘ │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Contracts (Ports & Models)        │
│  ┌────────────────────────────────────┐ │
│  │  Abstract Interfaces & Data Models │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Key Components

#### Ports ([src/discord_bot/contracts/ports.py](src/discord_bot/contracts/ports.py))

Abstract interfaces defining contracts between layers:

- **[`DatabasePort`](src/discord_bot/contracts/ports.py)**: Database operations interface

  - `get_data()`: Fetch data from tables with query parameters
  - `insert_data()`: Insert new records
  - `update_data()`: Update existing records
  - `delete_data()`: Remove records
  - `get_random_entry()`: Fetch random entries by category
  - `get_table_size()`: Get count of entries in a table
- **[`ModelPort`](src/discord_bot/contracts/ports.py)**: Base interface for business logic models

  - `logging()`: Log model activities
  - `execute_function()`: Execute model-specific operations
- **[`TranslatePort`](src/discord_bot/contracts/ports.py)**: Translation service interface (In Development)

  - Supports both single-message and auto-translation modes
  - Uses method overloading for different translation scenarios
- **[`FunFactPort`](src/discord_bot/contracts/ports.py)**: Fun facts retrieval interface

  - `execute_function()`: Fetches random fun facts from the database
- **[`DishPort`](src/discord_bot/contracts/ports.py)**: Dish suggestion interface

  - `execute_function(category)`: Suggests dishes based on categories
- **[`ControllerPort`](src/discord_bot/contracts/ports.py)**: Command handling interface (Planned)

  - `handle_command()`: Process Discord commands
  - `handle_message()`: Process Discord messages
  - `get_server_info()`: Retrieve server information
- **[`ViewPort`](src/discord_bot/contracts/ports.py)**: UI rendering interface

  - `render_interface()`: Render the web interface
  - `get_user_input()`: Capture user interactions

#### Adapters

Concrete implementations of ports:

- **[DBMS](src/discord_bot/adapters/db.py)**: MongoDB database adapter

  - Implements `DatabasePort` using PyMongo
  - Handles connection management and CRUD operations
  - Supports random entry selection using NumPy
- **[DiscordBotView](src/discord_bot/adapters/view.py)**: Gradio web interface adapter

  - Implements `ViewPort` using Gradio framework
  - Provides web dashboard for bot interaction
  - Supports server selection, channel messaging, and real-time feedback

#### Business Logic

Core application logic in [src/discord_bot/business_logic/](src/discord_bot/business_logic/):

- **[FunFactSelector](src/discord_bot/business_logic/fun_fact_selector.py)**: Retrieves random fun facts
- **[DishSelector](src/discord_bot/business_logic/dish_selector.py)**: Suggests dishes by category
- **[Translator](src/discord_bot/business_logic/translator.py)**: Translation service (stub implementation)
- **[Model](src/discord_bot/business_logic/model.py)**: Base class for business logic components

#### Initialization

Configuration and setup modules in [src/discord_bot/init/](src/discord_bot/init/):

- **[config_loader.py](src/discord_bot/init/config_loader.py)**: Loads configuration from `config.ini` and generates `.env` file
- **[db_loader.py](src/discord_bot/init/db_loader.py)**: Initializes database with CSV data from `db_data/`

## Project Structure

```
swp_discrod_bot_EMP/
├── src/
│   └── discord_bot/
│       ├── __init__.py
│       ├── adapters/              # External interface implementations
│       │   ├── __init__.py
│       │   ├── db.py              # MongoDB database adapter (DBMS)
│       │   ├── view.py            # Gradio web interface adapter
│       │   └── controller/        # Controller implementations (planned)
│       │       └── __init__.py
│       ├── app/                   # Application entry point
│       │   ├── __init__.py
│       │   └── main.py            # Main application for testing
│       ├── business_logic/        # Core business rules
│       │   ├── __init__.py
│       │   ├── model.py           # Base Model class
│       │   ├── fun_fact_selector.py  # Fun fact retrieval logic
│       │   ├── dish_selector.py   # Dish suggestion logic
│       │   └── translator.py      # Translation logic (stub)
│       ├── contracts/             # Ports and models
│       │   ├── __init__.py
│       │   ├── models.py          # Pydantic data models (empty)
│       │   └── ports.py           # Abstract interfaces
│       ├── init/                  # Initialization and setup
│       │   ├── __init__.py
│       │   ├── config_loader.py   # Config and .env generation
│       │   ├── db_loader.py       # Database initialization
│       │   └── db_data/           # CSV data files
│       │       ├── dishes.csv
│       │       └── fun_facts.csv
│       ├── dummies/               # Mock implementations for testing
│       ├── test_contracts/        # Contract tests
│       ├── test_flows/            # Integration tests
│       └── dockerfile             # Docker configuration for Gradio service
├── tests/                         # Test suite
├── config.ini                     # Application configuration
├── docker-compose.yaml            # Docker Compose configuration
├── start.bat                      # Windows startup script
├── .gitignore                     # Git ignore rules
├── LICENSE                        # Project license
├── pyproject.toml                 # Project configuration and dependencies
└── README.md                      # This file
```

## Quick Start

The easiest way to get started on Windows is using the provided `start.bat` script:

1. **Configure the bot** (first time only)

   - Edit `config.ini` with your settings:
     - MongoDB credentials
     - Mongo Express credentials
     - Discord bot token (optional for now)
2. **Run the startup script**

   ```cmd
   start.bat
   ```

The `start.bat` script will automatically:

- Create a Python virtual environment (`.venv`) if it doesn't exist
- Activate the virtual environment
- Ask if you want to install dev dependencies
- Install the project and its dependencies from `pyproject.toml`
- Generate the `.env` file from `config.ini`
- Start Docker services (MongoDB and Mongo Express)
- Initialize the database with sample data from CSV files

3. **Access the services**
   - **Gradio Web Interface**: http://localhost:7860
   - **Mongo Express**: http://localhost:8081 (login with credentials from `config.ini`)
   - **MongoDB**: mongodb://localhost:27017

## Installation

### Prerequisites

- **Python** >= 3.11
- **Docker Desktop** (for containerized services)
- **pip** package manager
- **Git** (for cloning the repository)

### Manual Setup (Alternative to start.bat)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd swp_discrod_bot_EMP
   ```
2. **Configure the application**

   - Edit `config.ini` with your configuration

   ```ini
   [database]
   db_name = swp_discord_bot_emp
   mongo_root_user = admin
   mongo_root_password = admin

   [mongo_express]
   basic_auth_username = admin
   basic_auth_password = admin

   [discord]
   discord_token = #your_bot_token_here
   ```
3. **Create and activate virtual environment**

   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/macOS
   python -m venv .venv
   source .venv/bin/activate
   ```
4. **Install the package**

   ```bash
   # Standard installation
   pip install -e .

   # With development dependencies
   pip install -e .[dev]
   ```
5. **Generate .env file**

   ```bash
   python src/discord_bot/init/config_loader.py
   ```
6. **Start Docker services**

   ```bash
   docker-compose up -d
   ```
7. **Initialize database**

   ```bash
   python src/discord_bot/init/db_loader.py
   ```

## Configuration

The application is configured through `config.ini`, which is then converted to a `.env` file for Docker services.

### config.ini Structure

```ini
[database]
db_name = swp_discord_bot_emp
mongo_root_user = admin
mongo_root_password = admin

[mongo_express]
basic_auth_username = admin
basic_auth_password = admin

[discord]
discord_token = #your_bot_token_here
```

The `.env` file is automatically generated from `config.ini` by running:

```bash
python src/discord_bot/init/config_loader.py
```

Or simply by using `start.bat`.

### Project Configuration

The project uses [pyproject.toml](pyproject.toml) for Python package configuration:

- **Python Version**: >= 3.11
- **Main Dependencies**:

  - `pydantic>=2.0` - Data validation using Python type annotations
  - `gradio>=4.0` - Web interface framework
  - `multipledispatch>=0.6` - Multiple dispatch for Python
  - `pymongo>=4.0` - MongoDB driver for Python
- **Development Tools**:

  - `mypy>=1.0` - Static type checker
  - `build>=1.2` - Build tool
  - `pyinstaller>=6.0` - Package Python applications
  - `black>=23.0` - Code formatter (line-length: 120)
  - `ruff>=0.0` - Fast Python linter

## Usage

### Using start.bat (Recommended for Windows)

The `start.bat` script provides an all-in-one solution:

```cmd
start.bat
```

**What it does:**

1. Checks if virtual environment exists, creates one if not
2. Activates the virtual environment
3. Prompts to install dev dependencies (y/n)
4. Installs project dependencies from `pyproject.toml`
5. Generates `.env` file from `config.ini`
6. Starts Docker services (MongoDB + Mongo Express + Gradio)
7. Initializes database with sample data

### Running Components Individually

**Test the business logic:**

```bash
python src/discord_bot/app/main.py
```

This runs a simple test of `FunFactSelector` and `DishSelector`.

**Launch the Gradio web interface:**

```bash
python -m discord_bot.adapters.view
```

Access at: http://localhost:7860

**Initialize database manually:**

```bash
python src/discord_bot/init/db_loader.py
```

### Web Interface

The Gradio web dashboard at `http://localhost:7860` provides:

- Server selection dropdown
- Channel ID input
- Message sending interface
- Real-time output display

### Database Management

**Mongo Express** (http://localhost:8081):

- Browse collections (`dishes`, `fun_facts`)
- Add, edit, or delete entries
- View database statistics
- Login with credentials from `config.ini`

### Current Features

- **Fun Facts**: Retrieves random fun facts from the `fun_facts` collection
- **Dish Suggestions**: Suggests dishes by category from the `dishes` collection

**Example usage in code:**

```python
from discord_bot.adapters.db import DBMS
from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.business_logic.dish_selector import DishSelector

db = DBMS()
db.connect()

# Get a random fun fact
fun_fact_selector = FunFactSelector(dbms=db)
print(fun_fact_selector.execute_function())

# Get an Italian dish suggestion
dish_selector = DishSelector(dbms=db)
print(dish_selector.execute_function(category="Italian"))
```

## Development

### Code Style

This project follows PEP 8 guidelines with the following configurations:

**Black Formatter**:

- Line length: 120 characters
- Target Python version: 3.13

**Ruff Linter**:

- Line length: 120 characters
- Enabled rules: E (errors), F (pyflakes), W (warnings), C (complexity), Q (quotes)

Format code using:

```bash
black src/
```

Lint code using:

```bash
ruff check src/
```

### Type Checking

Run type checking with mypy:

```bash
mypy src/discord_bot
```

Configuration is specified in [pyproject.toml](pyproject.toml).

### Running Tests

```bash
pytest tests/
```

Run tests with coverage:

```bash
pytest --cov=discord_bot tests/
```

### Building the Project

Build distribution packages:

```bash
python -m build
```

This creates wheel and source distribution files in the `dist/` directory.

### Creating an Executable

Create a standalone executable with PyInstaller:

```bash
pyinstaller --onefile src/discord_bot/app/main.py
```

### Docker Services

The project uses Docker Compose to manage three services:

1. **MongoDB** (port 27017)

   - Database service
   - Persistent volume: `mongo_data`
   - Credentials from `.env` file
2. **Mongo Express** (port 8081)

   - Web-based MongoDB admin interface
   - Basic auth from `.env` file
3. **Gradio** (port 7860)

   - Web interface for the bot
   - Built from `src/discord_bot/dockerfile`
   - Source code mounted as volume for live development

**Managing Docker services:**

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild Gradio service after code changes
docker-compose up -d --build gradio
```

### Adding New Features

Follow these steps to add new features while maintaining clean architecture:

1. **Define the port interface** in [src/discord_bot/contracts/ports.py](src/discord_bot/contracts/ports.py)

   - Create an abstract base class inheriting from `ABC` and `ModelPort` (or appropriate base)
   - Define abstract methods with proper type hints and docstrings
2. **Create data models** in [src/discord_bot/contracts/models.py](src/discord_bot/contracts/models.py) (if needed)

   - Use Pydantic models for data validation
3. **Implement business logic** in [src/discord_bot/business_logic/](src/discord_bot/business_logic/)

   - Create a class inheriting from `Model` and your port interface
   - Keep business rules separate from external concerns
   - Depend only on port interfaces (e.g., `DatabasePort`), not concrete implementations
4. **Implement adapters** in [src/discord_bot/adapters/](src/discord_bot/adapters/) (if needed)

   - Create concrete classes implementing port interfaces
   - Handle external dependencies (API calls, database operations, etc.)
5. **Add database data** in [src/discord_bot/init/db_data/](src/discord_bot/init/db_data/)

   - Create CSV files with your data
   - Run `db_loader.py` to populate the database
6. **Add tests** (planned)

   - Contract tests in [src/discord_bot/test_contracts/](src/discord_bot/test_contracts/)
   - Integration tests in [src/discord_bot/test_flows/](src/discord_bot/test_flows/)
   - Unit tests in [tests/](tests/)
7. **Update documentation**

   - Add docstrings to all public methods
   - Update this README if necessary

## Docker Deployment

### Building and Running with Docker Compose

The application is fully containerized using Docker Compose:

```bash
# Start all services in detached mode
docker-compose up -d

# View service logs
docker-compose logs -f gradio
docker-compose logs -f mongo

# Stop all services
docker-compose down

# Remove volumes (deletes database data)
docker-compose down -v

# Rebuild and restart services
docker-compose up -d --build
```

### Docker Services Configuration

**MongoDB:**

- Image: `mongo:latest`
- Port: 27017
- Volume: `mongo_data` (persistent storage)
- Environment: Configured via `.env`

**Mongo Express:**

- Image: `mongo-express:latest`
- Port: 8081
- Depends on: `mongo`
- Basic Auth: Configured via `.env`

**Gradio:**

- Built from: `src/discord_bot/dockerfile`
- Base Image: `python:3.13.7-slim`
- Port: 7860
- Volume: Source code mounted at `/usr/src/discord_bot`
- Depends on: `mongo`

### Dockerfile

The Gradio service uses a custom Dockerfile:

```dockerfile
FROM python:3.13.7-slim
WORKDIR /usr/src/discord_bot

COPY . .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -e .[dev]

EXPOSE 7860
ENV GRADIO_SERVER_NAME=0.0.0.0
CMD ["python", "-m", "discord_bot.adapters.view"]
```

## API Documentation

### Port Interfaces

All port interfaces are defined in [src/discord_bot/contracts/ports.py](src/discord_bot/contracts/ports.py). Refer to the inline documentation for detailed method signatures and usage.

**Implemented Interfaces:**

- [`DatabasePort`](src/discord_bot/contracts/ports.py) - Database operations (implemented by `DBMS`)
- [`FunFactPort`](src/discord_bot/contracts/ports.py) - Fun facts (implemented by `FunFactSelector`)
- [`DishPort`](src/discord_bot/contracts/ports.py) - Dish suggestions (implemented by `DishSelector`)
- [`ViewPort`](src/discord_bot/contracts/ports.py) - UI rendering (implemented by `DiscordBotView`)

**Planned Interfaces:**

- [`TranslatePort`](src/discord_bot/contracts/ports.py) - Translation services
- [`ControllerPort`](src/discord_bot/contracts/ports.py) - Command handling

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**

   ```bash
   git fork <repository-url>
   ```
2. **Create a feature branch**

   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Make your changes**

   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation as needed
4. **Run tests and linting**

   ```bash
   pytest tests/
   black src/
   ruff check src/
   mypy src/discord_bot
   ```
5. **Commit your changes**

   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
6. **Push to the branch**

   ```bash
   git push origin feature/AmazingFeature
   ```
7. **Open a Pull Request**

   - Provide a clear description of the changes
   - Reference any related issues

### Contribution Guidelines

- Follow clean architecture principles
- Maintain separation of concerns
- Write comprehensive tests
- Document all public APIs
- Use type hints throughout
- Follow PEP 8 style guidelines

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## Authors

- **Emir Keser** - Database Layer - [ekeser@student.tgm.ac.at](mailto:ekeser@student.tgm.ac.at)
- **Mateja Gvozdenac** - View Layer - [mgvozdenac@student.tgm.ac.at](mailto:mgvozdenac@student.tgm.ac.at)
- **Paul Hinterbauer** - Business Logic - [phinterbauer@student.tgm.ac.at](mailto:phinterbauer@student.tgm.ac.at)

## Acknowledgments

- **TGM - Die Schule der Technik** - Educational institution
- **Discord.py** - Python wrapper for the Discord API
- **Pydantic** - Data validation using Python type annotations
- **Gradio** - Fast, easy way to create ML web apps
- **Clean Architecture** - Principles by Robert C. Martin
- **Hexagonal Architecture** - Ports and Adapters pattern

## Project Status

This is an active school project for the Software Project (SWP) course at TGM - Die Schule der Technik.

**Current Version**: 0.1.0

### Implementation Status

**Completed:**

- [✓] Clean Architecture foundation with ports and adapters
- [✓] MongoDB database layer (`DBMS` adapter)
- [✓] Gradio web interface (`DiscordBotView` adapter)
- [✓] Fun facts feature (`FunFactSelector`)
- [✓] Dish suggestion feature (`DishSelector`)
- [✓] Database initialization from CSV files
- [✓] Docker Compose setup with MongoDB and Mongo Express
- [✓] Configuration management system
- [✓] Windows startup script (`start.bat`)

**In Progress:**

- [~] Translation service (`Translator` - stub implementation)

**Planned:**

- [ ] Discord bot integration
- [ ] Controller layer for command handling
- [ ] Discord bot commands (!funfact, !dish, !translate)
- [ ] Comprehensive test suite
- [ ] Additional business logic features

### Development Timeline

- **Phase 1** (Completed): Architecture design and database layer
- **Phase 2** (Completed): Basic business logic and web interface
- **Phase 3** (Current): Discord bot integration and command handling
- **Phase 4** (Planned): Testing and refinement
- **Phase 5** (Planned): Documentation and deployment

---

**Note**: This is a school project developed for educational purposes at TGM - Die Schule der Technik.

For questions or support, please contact the development team or open an issue on the project repository.
