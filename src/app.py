from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from src.models import PostInputModel, PostModel, UpdateInputModel
from src.tasks import create_post_task, find_post_by_id, update_post_task, get_all_post, delete_post_task
from src.auth import auth_router, get_current_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


app.include_router(auth_router)


@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")


@app.post("/create_post", status_code=status.HTTP_201_CREATED, response_model=PostModel)
def create_post(new_post : PostInputModel,current_user: str = Depends(get_current_user)):
    
    post_dict = PostModel(
        author=current_user,
        title=new_post.title, 
        content=new_post.content 
    ) 
    post_dict.created_at = datetime.now().isoformat()
    post_dict.updated_at = post_dict.created_at
    
    post = post_dict.dict()
    task = create_post_task.apply_async(args=[post])
    result = task.get()
    if not result :
        raise HTTPException(status_code=400)
    return post_dict
    

@app.get("/get_posts")
def get_posts():
    task = get_all_post.apply_async()
    result =  task.get()
    if not result:
        raise HTTPException(status_code=404 , detail="No posts found")
    
    return result

@app.get("/get_post_by_id/{post_id}", 
         responses={
             200: {
                 "description": "Successful Response",
                 "content": {
                     "application/json": {
                         "example": {
                             "author": "user@example.com",
                             "title": "Example Post",
                             "content": "This is a sample post",
                             "created_at": "2025-01-24T11:06:37.248506",
                             "updated_at": "2025-01-24T11:06:37.248506"
                         }
                     }
                 }
             },
             404: {
                 "description": "Post not found",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Post not found"}
                     }
                 }
             },
             400: {
                 "description": "Invalid post ID format",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Invalid post ID format"}
                     }
                 }
             },
         })
def get_post_by_id(post_id: str):
    post = find_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/update_post_by_id/{post_id}",
         responses={
             200: {
                 "description": "Post successfully updated",
                 "content": {
                     "application/json": {
                         "example": {
                             "author": "user@example.com",
                             "title": "Updated Title",
                             "content": "Updated content",
                             "created_at": "2025-01-24T11:06:37.248506",
                             "updated_at": "2025-01-24T12:00:00.123456"
                         }
                     }
                 }
             },
             400: {
                 "description": "Invalid data provided",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Invalid title or content"}
                     }
                 }
             },
             403: {
                 "description": "Forbidden: You are not the author",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Forbidden: You are not the author"}
                     }
                 }
             },
             404: {
                 "description": "Post not found",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Post not found"}
                     }
                 }
             }
         })
def update_post_by_id(post_id: str, post_updated_data: UpdateInputModel, current_user: str = Depends(get_current_user)):
    user_email = current_user
    post = find_post_by_id(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if user_email != post["author"]:
        raise HTTPException(status_code=403, detail="Forbidden: You are not the author")

    if not post_updated_data.title or not post_updated_data.content:
        raise HTTPException(status_code=400, detail="Invalid title or content")

    task = update_post_task.apply_async(args=[post_id, post_updated_data.title, post_updated_data.content])
    updated_post = task.get()

    return updated_post




@app.delete("/delete_post_by_id/{post_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            responses={
                204: {"description": "Post successfully deleted"},
                403: {"description": "Forbidden: You are not the author"},
                404: {"description": "Post not found"},
            })
def delete_post_by_id(post_id :str , current_user: str = Depends(get_current_user)) :
    
    user_email = current_user
    
    post = find_post_by_id(post_id)
    
    if user_email == post["author"]:
        task = delete_post_task.apply_async(args=[post_id])
        result = task.get()
        if not result:
            raise HTTPException(status_code=404, detail="Post not found")

        return Response(status_code=204)
    else : 
        raise HTTPException(status_code=403)