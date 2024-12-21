from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from pymongo import MongoClient
import bcrypt
import jwt
import datetime
from typing import List, Optional
import os
import dotenv
from fastapi.middleware.cors import CORSMiddleware

dotenv.load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the specific domain of your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["leetcode_twitter"]
users_collection = db["users"]
tweets_collection = db["tweets"]


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

def verify_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

# Models
class SignupModel(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=8)

class LoginModel(BaseModel):
    username: str
    password: str

class TweetModel(BaseModel):
    content: str = Field(..., max_length=280)
    timestamp: float

@app.post("/signup")
async def signup(user: SignupModel):
    
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(credentials: LoginModel):
    user = users_collection.find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_jwt(str(user["_id"]))
    return {"message": "Login successful", "token": token}

@app.get("/search")
async def search_users(prefix: str, token: str = Header(None)):
    verify_jwt(token)
    users = users_collection.find({"username": {"$regex": f"^{prefix}", "$options": "i"}}, {"username": 1})
    return [user["username"] for user in users]

@app.post("/follow")
async def follow_user(target_username: str, token: str = Header(None)):
    payload = verify_jwt(token)
    user_id = payload.get("user_id")
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    target_user = users_collection.find_one({"username": target_username})

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    if target_username in user["following"]:
        raise HTTPException(status_code=400, detail="Already following this user.")

    users_collection.update_one({"_id": ObjectId(user_id)}, {"$push": {"following": target_username}})
    users_collection.update_one({"username": target_username}, {"$push": {"followers": user["username"]}})
    return {"message": "User followed successfully."}

@app.post("/unfollow")
async def unfollow_user(target_username: str, token: str = Header(None)):
    payload = verify_jwt(token)
    user_id = payload.get("user_id")
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if target_username not in user["following"]:
        raise HTTPException(status_code=400, detail="You are not following this user.")

    users_collection.update_one({"_id": ObjectId(user_id)}, {"$pull": {"following": target_username}})
    users_collection.update_one({"username": target_username}, {"$pull": {"followers": user["username"]}})
    return {"message": "User unfollowed successfully."}

@app.post("/tweet")
async def post_tweet(tweet: TweetModel, token: str = Header(None)):
    payload = verify_jwt(token)
    user_id = payload.get("user_id")
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    tweet_data = {
        "username": user["username"],
        "content": tweet.content,
        "timestamp": tweet.timestamp
    }
    tweets_collection.insert_one(tweet_data)
    return {"message": "Tweet posted successfully."}

@app.get("/feed")
async def get_feed(token: str = Header(None)):
    payload = verify_jwt(token)
    user_id = payload.get("user_id")
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    following = user["following"]
    tweets = tweets_collection.find({"username": {"$in": following}}).sort("timestamp", -1).limit(10)
    return [{"username": tweet["username"], "content": tweet["content"], "timestamp": tweet["timestamp"]} for tweet in tweets]


@app.get("/")
async def root():
    return {"message": "LeetCode API is running!"}
