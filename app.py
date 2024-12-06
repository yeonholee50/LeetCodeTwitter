from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from bson.objectid import ObjectId
from pymongo import MongoClient
import bcrypt
import jwt
import datetime
from typing import Dict
import os
import dotenv

dotenv.load_dotenv()
"""
comment out this part when delpoying
import config
MONGO_URI = config.MongoURI
SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
"""
MONGO_URI = os.environ.get("MONGO_URI")
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
# Setup FastAPI app
app = FastAPI()

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["design_twitter"]
users_collection = db["users"]

# JWT Configuration


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_jwt(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Models
class SignupModel(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginModel(BaseModel):
    email: EmailStr
    password: str

# Endpoints
@app.post("/signup")
async def signup(user: SignupModel):
    # Check if email already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email is already registered.")

    # Create user
    hashed_password = hash_password(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "followers": [],
        "following": []
    }
    result = users_collection.insert_one(user_data)
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

@app.post("/login")
async def login(credentials: LoginModel):
    user = users_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Generate JWT token
    token = create_jwt(str(user["_id"]))
    return {"message": "Login successful", "token": token}

@app.get('/')
async def root():
    return {"message": "Design Twitter API is running!"}