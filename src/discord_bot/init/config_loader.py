import configparser
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
config_path = project_root / "config.ini"

config = configparser.ConfigParser()
files_read = config.read(config_path)

class DBConfigLoader:
    IN_DOCKER = os.path.exists("/.dockerenv")

    TIMEZONE = config.get("docker", "timezone", fallback="Europe/Vienna")
    
    MONGO_ROOT_USER = config.get("mongo", "mongo_root_user", fallback="root")
    MONGO_ROOT_PASSWORD = config.get("mongo", "mongo_root_password", fallback="rot")

    BASIC_AUTH_USERNAME = config.get("mongo_express", "basic_auth_username", fallback="admin")
    BASIC_AUTH_PASSWORD = config.get("mongo_express", "basic_auth_password", fallback="admin")

    URI_DOCKER = f"mongodb://{MONGO_ROOT_USER}:{MONGO_ROOT_PASSWORD}@mongo:27017/"
    URI_LOCAL = f"mongodb://{MONGO_ROOT_USER}:{MONGO_ROOT_PASSWORD}@localhost:27017/"
    
    MONGO_URI = os.getenv("MONGO_URI", URI_DOCKER if IN_DOCKER else URI_LOCAL)
    
    CV_DB_NAME = os.getenv("CV_DB_NAME", config.get("database", "cv_db_name", fallback="constant_values"))
    DISCORD_DB_NAME = os.getenv("DISCORD_DB_NAME", config.get("database", "discord_db_name", fallback="discord"))
    
    @staticmethod
    def generate_env():
        env_path = project_root / ".env"
        
        env_content = f"""# Auto-generated from config.ini - Do not edit manually
# Regenerate by calling DatabaseConfig.generate_env()

# Docker Configuration
TZ={DBConfigLoader.TIMEZONE}

# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME={DBConfigLoader.MONGO_ROOT_USER}
MONGO_INITDB_ROOT_PASSWORD={DBConfigLoader.MONGO_ROOT_PASSWORD}

# Mongo Express Basic Auth
ME_CONFIG_BASICAUTH_USERNAME={DBConfigLoader.BASIC_AUTH_USERNAME}
ME_CONFIG_BASICAUTH_PASSWORD={DBConfigLoader.BASIC_AUTH_PASSWORD}

# Discord Configuration
DISCORD_TOKEN={DiscordConfigLoader.DISCORD_TOKEN}

# Settings
DEV_MODE={str(SettingsConfigLoader.DEV_MODE).lower()}
"""
        
        with open(env_path, "w") as file:
            file.write(env_content)
        
        print(f'Generated .env from config.ini at {env_path}')

class DiscordConfigLoader:
    TARGET_LANGUAGE = os.getenv("TARGET_LANGUAGE", config.get("discord", "target_language", fallback="en"))
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", config.get("discord", "discord_token", fallback=""))

class SettingsConfigLoader:
    DEV_MODE = os.getenv("DEV_MODE", config.getboolean("settings", "dev_mode", fallback=True))

if __name__ == "__main__":
    DBConfigLoader.generate_env()
