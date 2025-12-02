import os
import configparser
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
config_path = project_root / 'config.ini'

config = configparser.ConfigParser()
files_read = config.read(config_path)

class DatabaseConfig:
    IN_DOCKER = os.path.exists("/.dockerenv")
    
    MONGO_ROOT_USER = config.get('database', 'mongo_root_user', fallback='root')
    MONGO_ROOT_PASSWORD = config.get('database', 'mongo_root_password', fallback='example')

    URI_DOCKER = f"mongodb://{MONGO_ROOT_USER}:{MONGO_ROOT_PASSWORD}@mongo:27017/"
    URI_LOCAL = f"mongodb://{MONGO_ROOT_USER}:{MONGO_ROOT_PASSWORD}@localhost:27017/"
    
    MONGO_URI = os.getenv("MONGO_URI", URI_DOCKER if IN_DOCKER else URI_LOCAL)
    
    DB_NAME = os.getenv("DB_NAME", config.get('database', 'db_name', fallback='swp_discord_bot_emp'))
    
    @staticmethod
    def generate_env():
        env_path = project_root / '.env'
        
        env_content = f"""# Auto-generated from config.ini - Do not edit manually
# Regenerate by calling DatabaseConfig.generate_env()

# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME={DatabaseConfig.MONGO_ROOT_USER}
MONGO_INITDB_ROOT_PASSWORD={DatabaseConfig.MONGO_ROOT_PASSWORD}

# Mongo Express Basic Auth
ME_CONFIG_BASICAUTH_USERNAME={config.get('mongo_express', 'basic_auth_username', fallback='admin')}
ME_CONFIG_BASICAUTH_PASSWORD={config.get('mongo_express', 'basic_auth_password', fallback='pass')}

# Discord Configuration
DISCORD_TOKEN={config.get('discord', 'discord_token', fallback='')}
"""
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"Generated .env from config.ini at {env_path}")

class DiscordConfig:
    TARGET_LANGUAGE = os.getenv("TARGET_LANGUAGE", config.get('discord', 'target_language', fallback='en'))
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", config.get('discord', 'discord_token', fallback=''))

if __name__ == "__main__":
    DatabaseConfig.generate_env()
