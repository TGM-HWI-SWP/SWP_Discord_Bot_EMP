# SWP Discord Bot

A feature-rich Discord bot with a web interface, built using Clean Architecture principles. This school project demonstrates modern software engineering practices including hexagonal architecture, dependency inversion, and separation of concerns.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Translation Services**: Automatic message translation to multiple languages
  - Single-message translation
  - Auto-translation for all messages from a specific user
- **Fun Facts**: Fetch random fun facts from various categories
- **Dish Suggestions**: Get meal recommendations based on categories
- **Web Interface**: Manage and monitor your bot through a Gradio-powered web dashboard
- **Database Integration**: Persistent storage for bot data and configurations
- **Server Management**: Handle multiple Discord servers simultaneously
- **Clean Architecture**: Fully decoupled components following hexagonal architecture principles

## Architecture

This project follows **Clean Architecture** (Hexagonal Architecture) principles, separating concerns into distinct layers:

```
┌─────────────────────────────────────────┐
│          Adapters (External)            │
│  ┌────────────┬────────────┬──────────┐ │
│  │ Controller │  Database  │   View   │ │
│  └────────────┴────────────┴──────────┘ │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Business Logic (Core)           │
│  ┌────────────────────────────────────┐ │
│  │  Application Use Cases & Rules     │ │
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

- **[`ModelPort`](src/discord_bot/contracts/ports.py)**: Base interface for AI/ML models
  - `logging()`: Log model activities
  - `execute_function()`: Execute model-specific operations

- **[`TranslatePort`](src/discord_bot/contracts/ports.py)**: Translation service interface
  - Supports both single-message and auto-translation modes
  - Uses method overloading for different translation scenarios

- **[`FunFactPort`](src/discord_bot/contracts/ports.py)**: Fun facts retrieval interface
  - Fetches random fun facts from the database

- **[`DishPort`](src/discord_bot/contracts/ports.py)**: Dish suggestion interface
  - Suggests dishes based on categories

- **[`ControllerPort`](src/discord_bot/contracts/ports.py)**: Command handling interface
  - `handle_command()`: Process Discord commands
  - `handle_message()`: Process Discord messages
  - `get_server_info()`: Retrieve server information

- **[`ViewPort`](src/discord_bot/contracts/ports.py)**: UI rendering interface
  - `render_interface()`: Render the web interface
  - `get_user_input()`: Capture user interactions

#### Adapters

Concrete implementations of ports located in [src/discord_bot/adapters/](src/discord_bot/adapters/):

- **Controller** ([src/discord_bot/adapters/controller/](src/discord_bot/adapters/controller/)): Command and message handling
  - [db.py](src/discord_bot/adapters/controller/db.py): Database adapter implementation
  - [view.py](src/discord_bot/adapters/controller/view.py): View adapter implementation

#### Business Logic

Core application logic and use cases located in [src/discord_bot/business_logic/](src/discord_bot/business_logic/)

#### Models

Data models defined in [src/discord_bot/contracts/models.py](src/discord_bot/contracts/models.py)

## Project Structure

```
swp_discrod_bot_EMP/
├── src/
│   └── discord_bot/
│       ├── __init__.py
│       ├── adapters/              # External interface implementations
│       │   └── controller/
│       │       ├── __init__.py
│       │       ├── db.py          # Database adapter
│       │       └── view.py        # View adapter
│       ├── app/                   # Application entry point
│       │   ├── __init__.py
│       │   └── main.py            # Main application entry
│       ├── business_logic/        # Core business rules
│       ├── contracts/             # Ports and models
│       │   ├── __init__.py
│       │   ├── models.py          # Pydantic data models
│       │   └── ports.py           # Abstract interfaces
│       ├── dummies/               # Mock implementations for testing
│       ├── test_contracts/        # Contract tests
│       └── test_flows/            # Integration tests
├── tests/                         # Test suite
├── .vscode/                       # VS Code configuration
│   └── settings.json
├── .gitignore                     # Git ignore rules
├── LICENSE                        # Project license
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation

### Prerequisites

- Python >= 3.11
- pip package manager
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd swp_discrod_bot_EMP
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install the package in development mode**
   ```bash
   pip install -e .
   ```

4. **Install development dependencies (optional)**
   ```bash
   pip install -e ".[dev]"
   ```

5. **Configure environment variables**
   ```bash
   # Create a .env file
   copy .env.example .env  # Windows
   cp .env.example .env    # macOS/Linux
   
   # Edit .env with your Discord token and other settings
   ```

## Configuration

Configure the bot by setting environment variables or editing the configuration file:

```env
DISCORD_TOKEN=your_bot_token_here
DATABASE_URL=your_database_url
LOG_LEVEL=INFO
```

### Project Configuration

The project uses [pyproject.toml](pyproject.toml) for configuration:

- **Python Version**: >= 3.11
- **Main Dependencies**:
  - `pydantic>=2.0` - Data validation using Python type annotations
  - `gradio>=4.0` - Web interface framework
  - `multipledispatch>=0.6` - Multiple dispatch for Python

- **Development Tools**:
  - `mypy>=1.0` - Static type checker
  - `build>=1.2` - Build tool
  - `pyinstaller>=6.0` - Package Python applications
  - `black>=23.0` - Code formatter
  - `ruff>=0.0` - Fast Python linter

## Usage

### Running the Bot

```bash
python src/discord_bot/app/main.py
```

Or, if installed:

```bash
python -m discord_bot.app.main
```

### Bot Commands

- `!translate <language> <message>` - Translate a message to the target language
- `!auto-translate <language>` - Enable auto-translation for all your messages
- `!funfact [category]` - Get a random fun fact (optionally filtered by category)
- `!dish <category>` - Get a dish suggestion based on category
- `!help` - Display available commands and usage information

### Web Interface

Access the Gradio web dashboard at `http://localhost:7860` (default port) to:
- Monitor bot activity in real-time
- Manage server configurations
- View logs and statistics
- Interact with bot features through a user-friendly interface

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

### Adding New Features

Follow these steps to add new features while maintaining clean architecture:

1. **Define the port interface** in [src/discord_bot/contracts/ports.py](src/discord_bot/contracts/ports.py)
   - Create an abstract base class inheriting from `ABC`
   - Define abstract methods with proper type hints and docstrings

2. **Create data models** in [src/discord_bot/contracts/models.py](src/discord_bot/contracts/models.py)
   - Use Pydantic models for data validation

3. **Implement the adapter** in [src/discord_bot/adapters/](src/discord_bot/adapters/)
   - Create a concrete class implementing the port interface
   - Handle external dependencies (API calls, database operations, etc.)

4. **Implement business logic** in [src/discord_bot/business_logic/](src/discord_bot/business_logic/)
   - Keep business rules separate from external concerns
   - Depend only on port interfaces, not concrete implementations

5. **Add tests**
   - Contract tests in [src/discord_bot/test_contracts/](src/discord_bot/test_contracts/)
   - Integration tests in [src/discord_bot/test_flows/](src/discord_bot/test_flows/)
   - Unit tests in [tests/](tests/)

6. **Update documentation**
   - Add docstrings to all public methods
   - Update this README if necessary

## API Documentation

### Port Interfaces

All port interfaces are defined in [src/discord_bot/contracts/ports.py](src/discord_bot/contracts/ports.py). Refer to the inline documentation for detailed method signatures and usage.

Key interfaces:
- [`DatabasePort`](src/discord_bot/contracts/ports.py) - Database operations
- [`TranslatePort`](src/discord_bot/contracts/ports.py) - Translation services
- [`FunFactPort`](src/discord_bot/contracts/ports.py) - Fun facts
- [`DishPort`](src/discord_bot/contracts/ports.py) - Dish suggestions
- [`ControllerPort`](src/discord_bot/contracts/ports.py) - Command handling
- [`ViewPort`](src/discord_bot/contracts/ports.py) - UI rendering

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

This is an active school project for the Software Project (SWP) course at TGM.

**Current Version**: 0.1.0

### Roadmap

- [ ] Implement Discord bot commands
- [ ] Complete database layer
- [ ] Build Gradio web interface
- [ ] Add translation service integration
- [ ] Implement fun facts feature
- [ ] Add dish suggestion feature
- [ ] Write comprehensive tests
- [ ] Deploy to production

---

**Note**: This is a school project developed for educational purposes at TGM - Die Schule der Technik.

For questions or support, please contact the development team or open an issue on the project repository.