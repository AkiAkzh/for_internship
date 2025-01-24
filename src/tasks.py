from datetime import datetime
from celery import Celery
from src.db import get_posts_collection, get_users_collection
from dotenv import load_dotenv
from bson import ObjectId
from .models import PostOutPutModel, UpdateInputModel
import os

load_dotenv()

celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_BROKER","redis://localhost:6379/0"),
    backend=os.getenv("REDIS_BACKEND", "redis://localhost:6379/0")
)

posts_collection = get_posts_collection()
users_collection = get_users_collection()


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
        return True
    else:
        return False
    # return {"_id": str(result.inserted_id), "message": "Post created asynchronously"}


@celery_app.task
def get_all_post():
    posts = list(posts_collection.find())
    for post in posts:
        post["_id"] = str(post["_id"])  
    print(posts)
    return posts

@celery_app.task
def find_post_by_id(post_id):
    post : PostOutPutModel = posts_collection.find_one({"_id" : ObjectId(post_id)})
    if not post:
        return None  
    post["_id"] = str(post["_id"])  
    return post

@celery_app.task
def update_post_task(post_id, title, content):
    updated_at = datetime.now()
    post_updated_data = UpdateInputModel(title=title, content=content, updated_at = updated_at )
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

@celery_app.task
def get_user_by_email(email : str):
    result = users_collection.find_one({"email" : email})
    if not result : 
        return None
    result["_id"] = str(result["_id"])
    return result


@celery_app.task
def user_create(email : str, username:str,hashed_password : str):
    result = users_collection.insert_one({"email" : email , "username" : username, "password" : hashed_password})
    
    created_user = {
        "email": email,
        "_id": str(result.inserted_id)
    }
    return created_user
