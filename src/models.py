from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from bson import ObjectId

class PostInputModel(BaseModel):
    title: str
    content: str

class PostModel(BaseModel):
    author: str
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now, example="2025-01-24T11:06:37.248506", description="Date format: YYYY-MM-DDTHH:MM:SS.mmmmmm")
    updated_at: datetime = Field(default_factory=datetime.now, example="2025-01-24T11:06:37.248506", description="Date format: YYYY-MM-DDTHH:MM:SS.mmmmmm")


class PostOutPutModel(BaseModel):
    _id : ObjectId
    author: str
    title: str
    content: str
    created_at: datetime 
    updated_at: datetime 

class UpdateInputModel(BaseModel):
    title : str
    content : str

class RegistrationInputModel(BaseModel) :
    email : EmailStr
    username : str
    password : str



class LoginInputModel(BaseModel):
    email : EmailStr
    password : str
