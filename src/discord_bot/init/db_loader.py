"""Load initial data from CSV files into MongoDB-backed tables."""

import csv
from pathlib import Path
from datetime import datetime

from discord_bot.adapters.db import DBMS
from discord_bot.init.config_loader import DBConfigLoader

class DBLoader:
    """Load initial data from CSV files into MongoDB-backed tables."""
    def __init__(self):
        self.cv_dbms = DBMS(db_name=DBConfigLoader.CV_DB_NAME)
        self.discord_dbms = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
        self.db_data_path = Path(__file__).parent / "db_data"
    
    def import_tables(self, force_reload: bool = False) -> None:
        """Import constant-value tables from CSV files into the CV database.

        Args:
            force_reload (bool): If True, always reload all tables even when data exists.
        """
        self.cv_dbms.connect()

        for csv_file in self.db_data_path.glob("*.csv"):
            table_name = csv_file.stem

            if not force_reload:
                existing_count = self.cv_dbms.get_table_size(table_name)
                if existing_count > 0:
                    # Skip populated tables unless a force reload is explicitly requested.
                    print(f'Skipping "{table_name}" - already contains {existing_count} documents')
                    continue

            with open(csv_file, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                data = [
                    {key: value for key, value in row.items() if key != "_id"}
                    for row in reader
                ]

            self.cv_dbms.upload_table(DBConfigLoader.CV_DB_NAME, table_name, data)
            print(f'Imported "{table_name}" - {len(data)} documents')
        
        print("Constant values database initialization complete")
    
    def initialize_discord_tables(self) -> None:
        """Initialize empty tables and statistics documents for the Discord database."""
        self.discord_dbms.connect()

        tables = ["messages", "direct_messages", "commands", "statistics", "auto_translate"]

        for table_name in tables:
            existing_count = self.discord_dbms.get_table_size(table_name)
            if existing_count == 0:
                self.discord_dbms.insert_data(table_name, {"_init": True})
                self.discord_dbms.delete_data(table_name, {"_init": True})
                print(f'Initialized empty table "{table_name}"')
            else:
                print(f'Table "{table_name}" already exists with {existing_count} documents')
        
        today = datetime.now().date().isoformat()
        existing_stats = self.discord_dbms.get_data("statistics", {"date": today})
        if not existing_stats:
            initial_stats = {
                "date": today,
                "total_messages": 0,
                "total_commands": 0,
                "total_dms": 0,
                "connected_guilds": 0,
                "command_breakdown": {},
            }
            # Seed a baseline statistics row so counters can be incremented safely.
            self.discord_dbms.insert_data("statistics", initial_stats)
            print(f'Initialized statistics for {today}')
        
        print("Discord database initialization complete")

if __name__ == "__main__":
    loader = DBLoader()
    loader.import_tables()
    loader.initialize_discord_tables()
