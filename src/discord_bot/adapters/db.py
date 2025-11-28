from pymongo import MongoClient
import numpy as np

from discord_bot.contracts.ports import DatabasePort

LOCAL = False

if LOCAL:
    Mongo_URI = "mongodb://localhost:27017/" 
    DB_NAME = "Test" 
else:
    Mongo_URI =  "mongodb+srv://admin:admin@discord-bot.ps1eipx.mongodb.net/"
    DB_NAME = "discord_bot_db"


client = MongoClient(Mongo_URI)
db= client[DB_NAME]

users_collection = db["users"]
servers_collection = db["servers"]
command_logs_collection = db["command_logs"]
funfacts_collection = db["funfacts"]
auto_translate_collection = db["auto_translate"]
dishes_collection = db["dishes"]


users_collection.insert_one({
    "username": "example_user",
    "role": "member"})


funfacts_collection.insert_one({
    "Text": "Did you know? The Eiffel Tower can be 15 cm taller during the summer, due to the expansion of iron in the heat.",
    "Text": "Bananas are berries, but strawberries arent. Botanically speaking, bananas qualify as berries—while strawberries do not!",
    "Text": "A day on Venus is longer than a year on Venus. Venus rotates so slowly that one full rotation takes longer than its orbit around the Sun.",
    "Text": "Honey never spoils. Archaeologists have found perfectly edible honey in ancient Egyptian tombs.",
    "Text": "Octopuses have three hearts. Two pump blood to the gills, and one pumps it to the rest of the body.",
    "Text": "There are more stars in the universe than grains of sand on all Earths beaches. The observable universe contains an estimated 1,000,000,000,000,000,000,000,000 stars."})


class DBMS(DatabasePort):
    def __init__(self):
        ...

    def get_table_size(self, table: str) -> int:
        collection = db[table]
        return collection.count_documents({})
    
    def get_random_entry(self, table: str, category: str | None) -> dict:
        table_size = self.get_table_size(table)
        random_index = np.random.randint(0, table_size)
        collection = db[table]
        random_entry = collection.find().limit(1).skip(random_index)
        for entry in random_entry:
            return entry
        
    def get_data(self, table: str, query: dict) -> list[dict]:
        collection = db[table]
        results = collection.find(query)
        return [result for result in results]
    
    def insert_data(self, table: str, data: dict) -> bool:
        collection = db[table]
        result = collection.insert_one(data)
        return result.acknowledged
    
    def update_data(self, table: str, query: dict, data: dict) -> bool:
        collection = db[table]
        result = collection.update_many(query, {"$set": data})
        return result.acknowledged
    
    def delete_data(self, table: str, query: dict) -> bool:
        collection = db[table]
        result = collection.delete_many(query)
        return result.acknowledged