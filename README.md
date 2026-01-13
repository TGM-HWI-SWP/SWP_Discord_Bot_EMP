            -----      -----            
         ----------------------         
        ------------------------        
       --------------------------       
      ----------------------------      
      --------   ------   --------      
      --------   ------   --------      
      ----------------------------      
      ----------------------------      
      ----------------------------      
         -----            -----         

# SWP Discord Bot EMP

A feature-rich Discord bot built with Python and Docker, providing entertainment and utility features including fun facts, dish suggestions, multi-language translation, and comprehensive message logging capabilities.

---

## About

This project was developed as part of the Software Project (SWP) course at TGM - Die Schule der Technik, Vienna, Austria (2025).

**Project Team:**
- Mateja Gvozdenac
- Emir Keser
- Paul Hinterbauer

---

## Features

- **Fun Facts** - Share interesting trivia with your community
- **Dish Suggestions** - Get meal recommendations
- **Translation** - Multi-language translation support
- **Auto-Translate** - Automatic translation for users
- **Message Logging** - Comprehensive message tracking
- **Statistics** - Server and user analytics
- **Admin Control Panel** - Web-based management interface

---

## Prerequisites

Before installing the bot, ensure you have the following:

- **Python 3.13** - [Download from python.org](https://www.python.org/downloads/release/python-3130/) or install via the Microsoft Store
- **Docker Desktop** - Required for containerized deployment
- **Discord Bot Application** - With proper permissions configured

---

## Installation

### 1. Download the Project

Clone the repository from GitHub:

```bash
git clone https://github.com/your-repo/SWP_Discord_Bot_EMP.git
```

Alternatively, download the repository as a `.zip` file directly from GitHub and extract it to your desired location.

### 2. Install Docker Desktop

Download and install Docker Desktop from the official website:

- [Docker Desktop Download](https://www.docker.com/products/docker-desktop)

Ensure Docker Desktop is running before proceeding to the next steps.

### 3. Create and Configure Discord Bot

Follow the official Discord documentation to create your bot application and obtain your bot token:

- [Discord Developer Documentation](https://discord.com/developers/docs/getting-started)

**Important:** On the Discord Developer Dashboard, you must enable the following **Privileged Gateway Intents** for your bot:

- **Presence Intent**
- **Server Members Intent**
- **Message Content Intent**

Refer to the Discord documentation for instructions on enabling these permissions in the Bot settings section.

### 4. Configure the Bot

1. Open the `config.ini` file in the project root directory
2. Add your Discord bot token to the `discord_token` field under the `[discord]` section
3. (Optional) Adjust other configuration values as needed, such as:
   - Target language for translations
   - Database credentials
   - MongoDB settings

### 5. Run the Bot

1. Navigate to the project directory in your file explorer
2. Right-click on the project folder and select **"Open in Terminal"**
3. Execute the startup script:

   ```bash
   .\start.bat
   ```

4. Wait for the setup process to complete - the bot will automatically initialize the database and start all required services

---

## Usage

### Discord Commands

Once the bot is invited to your server, you can use various slash commands:

- `/funfact` - Get a random fun fact
- `/dish` - Receive a meal suggestion
- And more...

### Admin Control Panel

Access the web-based admin control panel at:

- [http://localhost:7860](http://localhost:7860)

Manage bot settings, view statistics, and control bot behavior through the intuitive web interface.

### Database Management

For advanced users, direct database access is available via Mongo Express at:

- [http://localhost:8081](http://localhost:8081)

Use the credentials specified in your `config.ini` file to log in.

---

## License

This project is licensed under the terms specified in the `LICENSE` file.

**Note:** Please refer to the **EDUCATIONAL PROJECT NOTICE** section within the LICENSE file for additional information regarding the educational nature of this project.
