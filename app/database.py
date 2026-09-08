from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(MONGO_URL)

database = client["taskflow"]

users_collection = database["users"]
projects_collection = database["projects"]
tasks_collection = database["tasks"]
media_collection = database["media"]


def check_database():
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False