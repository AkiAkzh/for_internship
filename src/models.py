from pydantic import BaseModel, EmailStr
from datetime import datetime
from bson import ObjectId

class PostInputModel(BaseModel):
    title: str
    content: str

class PostModel(BaseModel):
    author: str
    title: str
    content: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

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
