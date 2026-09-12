from pymongo import MongoClient
from app.config import MONGO_URL

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