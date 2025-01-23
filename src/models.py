from pydantic import BaseModel
from datetime import datetime

class PostModel(BaseModel):
    author: str
    title: str
    content: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class UpdateInputModel(BaseModel):
    title : str
    content : str

class UpdateModel(BaseModel):
    title: str
    content: str
    updated_at: datetime = datetime.now()
