from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from bson import ObjectId
import bcrypt
import jwt
import datetime
from typing import List
import os
import dotenv

dotenv.load_dotenv()

# Load environment variables
MONGO_URI = os.environ.get("MONGO_URI")
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

app = FastAPI()

# MongoDB Connection using Motor (asynchronous)
import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.get_database("leetcode_twitter")
users_collection = db.get_collection("users")
tweets_collection = db.get_collection("tweets")

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_jwt(user_id: str) -> str:
    payload = {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

# Models
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            return v
        raise ValueError("Invalid ObjectId")

class UserOutModel(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str
    followers: List[str] = []
    following: List[str] = []

    class Config:
        json_encoders = {ObjectId: str}

class SignupModel(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=8)

class LoginModel(BaseModel):
    username: str
    password: str

class TweetModel(BaseModel):
    content: str = Field(..., max_length=280)
    timestamp: float

# Signup Endpoint
@app.post("/signup")
async def signup(user: SignupModel):
    if await users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username is already taken.")

    hashed_password = hash_password(user.password)
    user_data = {
        "username": user.username,
        "hashed_password": hashed_password,
        "followers": [],
        "following": []
    }

    result = await users_collection.insert_one(user_data)
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

# Login Endpoint
@app.post("/login")
async def login(credentials: LoginModel):
    user = await users_collection.find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_jwt(str(user["_id"]))
    return {"message": "Login successful", "token": token}

# Get User Profile
@app.get("/profile", response_model=UserOutModel)
async def get_profile(token: str = Header(None)):
    payload = verify_jwt(token)
    user_id = payload.get("user_id")

    user = await users_collection.find_one({"_id": ObjectId(user_id)}, {"hashed_password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return user

# Post Tweet
@app.post("/tweet")
async def post_tweet(tweet: TweetModel, token: str = Header(None)):
    payload = verify_jwt(token)
    user_id = payload.get("user_id")

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    tweet_data = {
        "username": user["username"],
        "content": tweet.content,
        "timestamp": tweet.timestamp
    }
    await tweets_collection.insert_one(tweet_data)
    return {"message": "Tweet posted successfully."}

# Get Feed
@app.get("/feed")
async def get_feed(token: str = Header(None)):
    payload = verify_jwt(token)
    user_id = payload.get("user_id")

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    following = user["following"]
    tweets = await tweets_collection.find({"username": {"$in": following}}).sort("timestamp", -1).to_list(10)
    return tweets

@app.get("/")
async def root():
    return {"message": "LeetCode API is running!"}
