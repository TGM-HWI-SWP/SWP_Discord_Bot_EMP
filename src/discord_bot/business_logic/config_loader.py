import os
import configparser
from pathlib import Path

config_path = Path(__file__).parent.parent.parent / 'config.ini'
config = configparser.ConfigParser()
config.read(config_path)

class DatabaseConfig:
    IN_DOCKER = os.path.exists("/.dockerenv")
    
    MONGO_ROOT_USER = config.get('database', 'mongo_root_user', fallback='root')
    MONGO_ROOT_PASSWORD = config.get('database', 'mongo_root_password', fallback='example')
    
    URI_DOCKER = config.get('database', 'uri_docker', fallback='mongodb://root:example@mongo:27017/')
    URI_LOCAL = config.get('database', 'uri_local', fallback='mongodb://root:example@localhost:27017/')
    
    MONGO_URI = os.getenv("MONGO_URI", URI_DOCKER if IN_DOCKER else URI_LOCAL)
    
    DB_NAME = os.getenv("DB_NAME", config.get('database', 'db_name', fallback='swp_discord_bot'))
    
    @staticmethod
    def generate_env():
        env_path = Path(__file__).parent.parent.parent / '.env'
        
        env_content = f"""# Auto-generated from config.ini - Do not edit manually
# Regenerate by calling DatabaseConfig.generate_env()

# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME={DatabaseConfig.MONGO_ROOT_USER}
MONGO_INITDB_ROOT_PASSWORD={DatabaseConfig.MONGO_ROOT_PASSWORD}
DB_NAME={DatabaseConfig.DB_NAME}

# Discord Configuration
DISCORD_TOKEN={config.get('discord', 'discord_token', fallback='')}
"""
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"Generated .env from config.ini at {env_path}")

class DiscordConfig:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", config.get('discord', 'discord_token', fallback=''))
