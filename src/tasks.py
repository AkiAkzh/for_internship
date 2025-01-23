from datetime import datetime
import logging
from celery import Celery
from src.db import mongo_start
from dotenv import load_dotenv
from bson import ObjectId
from .models import UpdateModel
import os

load_dotenv()

celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_BROKER","redis://localhost:6379/0"),
    backend=os.getenv("REDIS_BACKEND", "redis://localhost:6379/0")
)

posts_collection = mongo_start()


@celery_app.task
def create_post_task(post_data):
    print(post_data)
    if not post_data:
        raise ValueError("No post data provided")
    if 'created_at' in post_data:
        post_data['created_at'] = datetime.fromisoformat(post_data['created_at'])
    if 'updated_at' in post_data:
        post_data['updated_at'] = datetime.fromisoformat(post_data['updated_at'])

    result = posts_collection.insert_one(post_data)

    if result:
        return {"_id": str(result.inserted_id), "message": "Post created successfully"}
    else:
        return {"message": "Error inserting post"}
    # return {"_id": str(result.inserted_id), "message": "Post created asynchronously"}


@celery_app.task
def get_all_post():
    posts = list(posts_collection.find())
    for post in posts:
        post["_id"] = str(post["_id"])  
    print(posts)
    return posts

@celery_app.task
def find_post_by_title(post_title : str):
    post = posts_collection.find_one({"title" : post_title})
    if not post:
        return None  
    post["_id"] = str(post["_id"])  
    return post

@celery_app.task
def update_post_task(post_id, title, content):
    updated_at = datetime.now()
    post_updated_data = UpdateModel(title=title, content=content, updated_at = updated_at )
    result = posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": post_updated_data.dict()}
    )
    if result.matched_count == 0:
        return {"message": "Post not found"}
    return {"message": "Post updated successfully"}

@celery_app.task
def delete_post_task(post_id):
    result = posts_collection.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        return {"message": "Post not found"}
    return {"message": "Post deleted successfully"}