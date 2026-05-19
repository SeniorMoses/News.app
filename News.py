from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import os
import jwt
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

env_path = Path(".env")
load_dotenv(env_path)

SECRET = os.getenv("SECRET")
DBURL = os.getenv("DBURL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = psycopg2.connect(DBURL, cursor_factory=RealDictCursor)
cursor = conn.cursor()

class Signup(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=8)

class Login(BaseModel):
    email: EmailStr
    password: str

class News(BaseModel):
    title: str
    content: str

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
id SERIAL PRIMARY KEY,
username TEXT NOT NULL,
email TEXT UNIQUE NOT NULL,
password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS news (
id SERIAL PRIMARY KEY,
title TEXT NOT NULL,
content TEXT NOT NULL,
created_at TIMESTAMP DEFAULT NOW()
)
""")

conn.commit()

def create_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed.encode())

@app.post("/signup")
def signup(data: Signup):
    hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (data.username, data.email, hashed)
        )
        conn.commit()
        return {"message": "user created"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(data: Login):
    cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user["email"])

    return {"access_token": token, "token_type": "bearer"}

auth = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/news")
def create_news(data: News, user=Depends(get_current_user)):
    cursor.execute(
        "INSERT INTO news (title, content) VALUES (%s, %s)",
        (data.title, data.content)
    )
    conn.commit()
    return {"message": "news created"}

@app.get("/news")
def get_news():
    cursor.execute("SELECT * FROM news ORDER BY id DESC")
    return cursor.fetchall()
