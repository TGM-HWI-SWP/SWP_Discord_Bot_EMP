import csv
from pathlib import Path
from datetime import datetime

from discord_bot.adapters.db import DBMS
from discord_bot.init.config_loader import DBConfigLoader

class DBLoader:
    def __init__(self):
        self.cv_dbms = DBMS(db_name=DBConfigLoader.CV_DB_NAME)
        self.discord_dbms = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
        self.db_data_path = Path(__file__).parent / "db_data"
    
    def import_collections(self, force_reload: bool = False):
        self.cv_dbms.connect()
        
        for csv_file in self.db_data_path.glob('*.csv'):
            collection_name = csv_file.stem

            if not force_reload:
                existing_count = self.cv_dbms.get_table_size(collection_name)
                if existing_count > 0:
                    print(f'Skipping \'{collection_name}\' - already contains {existing_count} documents')
                    continue

            with open(csv_file, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                data = [
                    {key: value for key, value in row.items() if key != "_id"}
                    for row in reader
                ]

            self.cv_dbms.upload_collection(DBConfigLoader.CV_DB_NAME, collection_name, data)
            print(f'Imported \'{collection_name}\' - {len(data)} documents')
        
        print("Constant values database initialization complete")
    
    def initialize_discord_collections(self):
        self.discord_dbms.connect()
        
        collections = ["messages", "direct_messages", "commands", "statistics", "auto_translate"]
        
        for collection_name in collections:
            existing_count = self.discord_dbms.get_table_size(collection_name)
            if existing_count == 0:
                self.discord_dbms.insert_data(collection_name, {"_init": True})
                self.discord_dbms.delete_data(collection_name, {"_init": True})
                print(f'Initialized empty collection \'{collection_name}\'')
            else:
                print(f'Collection \'{collection_name}\' already exists with {existing_count} documents')
        
        today = datetime.now().date().isoformat()
        existing_stats = self.discord_dbms.get_data("statistics", {"date": today})
        if not existing_stats:
            initial_stats = {
                "date": today,
                "total_messages": 0,
                "total_commands": 0,
                "total_dms": 0,
                "unique_users": 0,
                "unique_servers": 0,
                "command_breakdown": {}
            }
            self.discord_dbms.insert_data("statistics", initial_stats)
            print(f'Initialized statistics for {today}')
        
        print("Discord database initialization complete")

if __name__ == "__main__":
    loader = DBLoader()
    loader.import_collections()
    loader.initialize_discord_collections()
