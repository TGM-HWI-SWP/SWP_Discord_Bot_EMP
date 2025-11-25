from pymongo import MongoClient

Mongo_URI = "mongodb+srv://admin:<db_password>@discord-bot.ps1eipx.mongodb.net/"
DB_NAME = "discord_bot_db"#

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
