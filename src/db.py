from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()

MONGO_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv("MY_DB_NAME")
COLLECTION_NAME = os.getenv("MY_DB_COLLECTION")



def mongo_start():
    try:
        mongo_client = MongoClient(MONGO_URI)
        return mongo_client[DB_NAME][COLLECTION_NAME]
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None