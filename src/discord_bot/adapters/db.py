from pymongo import MongoClient
# from contracts.ports import DatabasePort

Mongo_URI = "mongodb://localhost:27017/" # "mongodb+srv://admin:<db_password>@discord-bot.ps1eipx.mongodb.net/"
DB_NAME = "Test" # "discord_bot_db"#

client = MongoClient(Mongo_URI)
db= client[DB_NAME]

users_collection = db["users"]
servers_collection = db["servers"]
command_logs_collection = db["command_logs"]
funfacts_collection = db["funfacts"]
auto_translate_collection = db["auto_translate"]
dishes_collection = db["dishes"]



users_collection.insert_one({
    "user_id": 123456789,
    "username": "example_user",
    "role": "member"})

funfacts_collection.insert_one({
    "id": 1 ,  
    "Text": "Did you know? The Eiffel Tower can be 15 cm taller during the summer, due to the expansion of iron in the heat."})



# class MongoDBAdapter(DatabasePort):
#     def get_user(self, user_id: int) -> dict | None:
#         return users_collection.find_one({"user_id": user_id})

#     def add_user(self, user_data: dict) -> None:
#         users_collection.insert_one(user_data)

#     def log_command(self, command_data: dict) -> None:
#         command_logs_collection.insert_one(command_data)

#     def get_fun_fact(self, fact_id: int) -> dict | None:
#         return funfacts_collection.find_one({"id": fact_id})
    
