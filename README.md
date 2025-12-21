# SWP Discord Bot EMP

A Discord bot built with Python, using Docker for easy deployment. Features include fun facts, dish suggestions, translation, and more.

This is a school project made by student of the TGM in Vienna (2025)

- Mateja Gvozdenac
- Emir Keser
- Paul Hinterbauer

## Installation

1. **Download the code**: Clone this repository from GitHub.
   ```
   git clone https://github.com/your-repo/SWP_Discord_Bot_EMP.git
   ```

   Or simply download the .zip file directly from GitHub

2. **Set up Docker Desktop**: Download and install Docker Desktop from the official website: https://www.docker.com/products/docker-desktop

3. **Configure Discord Bot**: Follow the official Discord documentation to create a bot and get your token: https://discord.com/developers/docs/getting-started

4. **Configure the bot**:
   - Edit `config.ini` and add your Discord token.
   - Change any other settings in the `config.ini` as you please. These are not necessary.

5. **Run the bot**:
   - Extract the .zip folder downloaded from GitHub
   - Right click the extracted Folder and click on `Run in Terminal`
   - Type `.\start.bat` and hit enter
   - Wait for the code to finish setting up

## Features

- Fun facts
- Dish suggestions
- Translation
- Auto-translate for users
- Message logging
- Statistics

## Usage

Invite the bot to your server and use commands like `/funfact`, `/dish`, etc.
And control the bot via the http://localhost:7860 Admin Control Panel

The Database can be accessed at http://localhost:8081 but this is only needed for experienced users.

## License

See LICENSE file.
(Also see EDUCATIONAL PROJECT NOTICE in LICENSE file)
