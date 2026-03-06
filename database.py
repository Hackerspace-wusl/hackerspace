import os
import certifi
from pymongo import MongoClient

_users_col = None


def init_mongodb(app):
    global _users_col
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable is not set")

    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=5000,
        tlsCAFile=certifi.where(),
    )
    db_mongo = client["hackerspace_auth"]
    _users_col = db_mongo["users"]

    try:
        client.admin.command("ping")
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")


def get_users_col():
    if _users_col is None:
        err = "MongoDB not initialized. Call init_mongodb(app) first."
        raise RuntimeError(err)
    return _users_col
