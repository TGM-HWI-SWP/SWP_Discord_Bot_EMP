import csv
from pathlib import Path

from discord_bot.adapters.db import DBMS
from discord_bot.init.config_loader import DatabaseConfig

class DBLoader:
    def __init__(self):
        self.dbms = DBMS()
        self.db_data_path = Path(__file__).parent / 'db_data'
    
    def import_collections(self, force_reload: bool = False):
        self.dbms.connect()
        
        for csv_file in self.db_data_path.glob('*.csv'):
            collection_name = csv_file.stem

            if not force_reload:
                existing_count = self.dbms.get_table_size(collection_name)
                if existing_count > 0:
                    print(f"Skipping '{collection_name}' - already contains {existing_count} documents")
                    continue

            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = [
                    {k: v for k, v in row.items() if k != '_id'}
                    for row in reader
                ]

            self.dbms.upload_collection(DatabaseConfig.CV_DB_NAME, collection_name, data)
            print(f"Imported '{collection_name}' - {len(data)} documents")
        
        print("Database initialization complete")

if __name__ == "__main__":
    loader = DBLoader()
    loader.import_collections()
