import csv
from pathlib import Path

from discord_bot.adapters.db import DBMS
from discord_bot.init.config_loader import DatabaseConfig

class DBLoader:
    def __init__(self):
        self.dbms = DBMS()
        self.db_data_path = Path(__file__).parent / 'db_data'
    
    def import_collections(self):
        self.dbms.connect()
        
        for csv_file in self.db_data_path.glob('*.csv'):
            collection_name = csv_file.stem

            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = [
                    {k: v for k, v in row.items() if k != '_id'}
                    for row in reader
                ]

            self.dbms.upload_collection(DatabaseConfig.DB_NAME, collection_name, data)
        
        print("Database initialization complete")

if __name__ == "__main__":
    loader = DBLoader()
    loader.import_collections()
