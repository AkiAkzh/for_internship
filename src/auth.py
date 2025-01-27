from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from src.models import RegistrationInputModel, LoginInputModel
from src.tasks import get_user_by_email, user_create
import os

load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

def get_password_hash(password : str):
    return pwd_context.hash(password)

def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        secret_key = os.getenv("SECRET_KEY")
        algorithm = os.getenv("ALGORITHM")
        payload = jwt.decode(token, key=secret_key, algorithms=algorithm)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")

def create_acces_token(data : dict, expires_delta : timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=int(os.getenv("ACCES_TOKEN_EXPIRE_MINUTES"))))
    to_encode.update({"exp": expire})
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    return jwt.encode(to_encode, key=secret_key, algorithm=algorithm)


@auth_router.post("/register",
                  status_code=status.HTTP_201_CREATED,
                  responses={
                      201: {"description": "User successfully registered"},
                      409: {"description": "User with this email already exists"},
                  })

def registration(user : RegistrationInputModel):
    task = get_user_by_email.apply_async(args=[user.email])
    existing_user = task.get()
    if existing_user is not None : 
        raise HTTPException(status_code=409, detail="User with this email already exists")
    
    hashed_password = get_password_hash(user.password)
    
    task2 = user_create.apply_async(args=[user.email, user.username, hashed_password])
    result = task2.get()
   
    result_dict = {
        "email": result["email"],
        "id": result["_id"]
    }
    
    access_token = create_acces_token({"sub": user.email})
    
    response = JSONResponse(status_code=201, content={"user": result_dict, "access_token": access_token})
    response.headers["Content-Length"] = str(len(response.body))
    return response

@auth_router.post("/login",
                  responses={
                      200: {"description": "Successful login"},
                      401: {"description": "Invalid credentials"},
                  })
def login(user : LoginInputModel):

    task = get_user_by_email.apply_async(args=[user.email])
    try:
        existing_user = task.get(timeout=5)  
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}"
        )

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"A user with the following email address {user.email} does not exist")
    
    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")
    
    access_token = create_acces_token({"sub" : user.email})
    return {"access_token" : access_token ,"token_type": "bearer" }
