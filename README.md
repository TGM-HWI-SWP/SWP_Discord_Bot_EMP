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
- [Contributing](#contributing)
- [License](#license)

## Features

- **Translation Services**: Automatic message translation to multiple languages
- **Fun Facts**: Fetch random fun facts from various categories
- **Dish Suggestions**: Get meal recommendations based on categories
- **Web Interface**: Manage and monitor your bot through a web dashboard
- **Database Integration**: Persistent storage for bot data and configurations
- **Server Management**: Handle multiple Discord servers simultaneously

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

- **Ports** ([`src/discord-bot/contracts/ports.py`](src/discord-bot/contracts/ports.py)): Abstract interfaces defining contracts
  - [`DatabasePort`](src/discord-bot/contracts/ports.py): Database operations interface
  - [`ModelPort`](src/discord-bot/contracts/ports.py): Base interface for AI/ML models
  - [`TranslatePort`](src/discord-bot/contracts/ports.py): Translation service interface
  - [`FunFactPort`](src/discord-bot/contracts/ports.py): Fun facts retrieval interface
  - [`DishPort`](src/discord-bot/contracts/ports.py): Dish suggestion interface
  - [`ControllerPort`](src/discord-bot/contracts/ports.py): Command handling interface
  - [`ViewPort`](src/discord-bot/contracts/ports.py): UI rendering interface

- **Adapters**: Concrete implementations of ports
  - Controller: Command and message handling
  - Database: Data persistence layer
  - View: User interface components

- **Business Logic**: Core application logic and use cases

## Project Structure

```
swp_discrod_bot_EMP/
├── src/
│   └── discord-bot/
│       ├── __init__.py
│       ├── adapters/           # External interface implementations
│       │   └── controller/
│       │       ├── db.py       # Database adapter
│       │       └── view.py     # View adapter
│       ├── app/                # Application entry point
│       │   └── main.py
│       ├── business_logic/     # Core business rules
│       ├── contracts/          # Ports and models
│       │   ├── models.py       # Data models
│       │   └── ports.py        # Abstract interfaces
│       ├── dummies/            # Mock implementations
│       ├── test_contracts/     # Contract tests
│       └── test_flows/         # Integration tests
├── tests/                      # Test suite
├── .gitignore
├── LICENSE
├── pyproject.toml             # Project configuration
├── requirements.txt           # Python dependencies
└── README.md
```

## Installation

### Prerequisites

- Python >= 3.11
- pip or poetry package manager
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
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   copy .env.example .env
   # Edit .env with your Discord token and other settings
   ```

## Configuration

Configure the bot by setting environment variables or editing the configuration file:

```env
DISCORD_TOKEN=your_bot_token_here
DATABASE_URL=your_database_url
LOG_LEVEL=INFO
```

## Usage

### Running the Bot

```bash
python src/discord-bot/app/main.py
```

### Bot Commands

- `!translate <language> <message>` - Translate a message
- `!funfact [category]` - Get a random fun fact
- `!dish <category>` - Get a dish suggestion
- `!help` - Display available commands

### Web Interface

Access the web dashboard at `http://localhost:8000` (when running) to:
- Monitor bot activity
- Manage server configurations
- View logs and statistics

## Development

### Running Tests

```bash
pytest tests/
```

### Type Checking

```bash
mypy src/discord-bot
```

### Code Style

This project follows PEP 8 guidelines. Format code using:
```bash
black src/
isort src/
```

### Adding New Features

1. Define the port interface in [`src/discord-bot/contracts/ports.py`](src/discord-bot/contracts/ports.py)
2. Create the adapter implementation in `src/discord-bot/adapters/`
3. Implement business logic in `src/discord-bot/business_logic/`
4. Add tests in `tests/`

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## Authors

- **Emir Keser** - Database
- **Mateja Gvozdenac** - View
- **Paul Hinterbauer** - Business Logic

## Acknowledgments

- Discord.py library
- Clean Architecture principles by Robert C. Martin
- TGM - Die Schule der Technik

---

**Note**: This is a school project for educational purposes.