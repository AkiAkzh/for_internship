from datetime import time
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from src.models import PostModel, UpdateInputModel
from src.tasks import create_post_task, update_post_task, get_all_post,find_post_by_title, delete_post_task
from src.db import mongo_start

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

posty = mongo_start()

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")




@app.post("/create_post")
def create_post(post : PostModel):
    post_dict = post.dict() 
    if 'created_at' in post_dict:
        post_dict['created_at'] = post_dict['created_at'].isoformat()
    if 'updated_at' in post_dict:
        post_dict['updated_at'] = post_dict['updated_at'].isoformat()
   
    task = create_post_task.apply_async(args=[post_dict])
    result = task.get()
    
    # if not result:
    #     raise HTTPException(status_code=404, detail="No posts found")
    return result
    

@app.get("/get_posts")
def get_posts():
    task = get_all_post.apply_async()
    result =  task.get()
    if not result:
        raise HTTPException(status_code=404 , detail="No posts found")
    
    return result

@app.get("/get_post_by_title/{post_title}")
def get_post_by_title(post_title: str):
    post = find_post_by_title(post_title)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/update_post_by_id/{post_id}")
def update_post_by_id(post_id: str, post_updated_data: UpdateInputModel):
    task = update_post_task.apply_async(args=[post_id, post_updated_data.title, post_updated_data.content])
    
    updated_post = task.get()
    if updated_post.get("message") == "Post not found":
        raise HTTPException(status_code=404, detail="Post not found")
    
    return updated_post


@app.delete("/delete_post_by_id/{post_id}")
def delete_post_by_id(post_id :str) :
    task = delete_post_task.apply_async(args=[post_id])
    result = task.get()
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")

    return Response(status_code=204)
    # return {"message": f"Post with id {post_id} deleted successfully."}

