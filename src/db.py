from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()

MONGO_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv("MY_DB_NAME")
POSTS_COLLECTION = os.getenv("MY_DB_COLLECTION")
USERS_COLLECTION = os.getenv("MY_DB_USERS_COLLECTION")


def get_mongo_client():
    try:
        return MongoClient(MONGO_URI)
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def get_posts_collection():
    client = get_mongo_client()
    return client[DB_NAME][POSTS_COLLECTION] if client else None

def get_users_collection():
    client = get_mongo_client()
    return client[DB_NAME][USERS_COLLECTION] if client else None