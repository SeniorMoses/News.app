from fastapi import FastAPI, HTTPException, Header , Depends  
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, EmailStr, Field 
import sqlite3 
import jwt
from datetime import datetime, timedelta 
import bcrypt
from dotenv import load_dotenv
from pathlib import Path
import os
from fastapi.middleware.cors import CORSMiddleware  
env_path=Path('.env')
load_dotenv(env_path) 


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Oauth2_scheme=OAuth2PasswordBearer(tokenUrl='login')
dburl=os.getenv('DBURL')
conn=sqlite3.connect(dburl, check_same_thread=False)
conn.row_factory=sqlite3.Row
cursor=conn.cursor()
class Signup (BaseModel):
    username:str=Field(min_length=3)
    email: EmailStr 
    password:str=Field(min_length=8)
class Login (BaseModel):
    email: EmailStr 
    password: str=Field(min_length=8)
class News(BaseModel):
    date: str
    title: str
    content: str 
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
role TEXT NOT NULL,
username TEXT NOT NULL,
email TEXT UNIQUE NOT NULL,
password TEXT NOT NULL) 
''') 

conn.commit() 
cursor.execute('''
CREATE TABLE IF NOT EXISTS news(
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT NOT NULL,
title TEXT NOT NULL,
content TEXT NOT NULL)
''')
conn.commit() 
SECRET=os.getenv('SECRET') 
def create_token(user):
    return jwt.encode(
        {
            'username':user['username'],
            'role':user['role'],
            'id':user['id'],
            'exp': datetime.utcnow() + timedelta(hours=1)
    },
    SECRET, 
    algorithm = 'HS256'       
    )
    
def get_user(token:str =Depends(Oauth2_scheme)): 
  
    try:
        data=jwt.decode(
        token,
        SECRET,
        algorithms=['HS256']
        ) 
        return data
    except jwt.ExpiredSignatureError:
        raise HTTPException(
        status_code=401,
        detail='token expired')
    except jwt.InvalidTokenError:
        raise HTTPException (
        status_code=401,
        detail='invalid token'
        ) 
        
        
        
@app.get('/')
def home():
    return {'message': 'fastapi server is running🚀'}
    
@app.post('/signup')
async def register (data: Signup):
    
    hashed=await run_in_threadpool(
     bcrypt.hashpw,
    data.password.encode(),
    bcrypt.gensalt()
     )
    try:
        cursor.execute(
        'INSERT INTO users (username, role, email, password) VALUES (?,?,?,?)', [data.username, 'user', data.email, hashed.decode()] 
    )
        conn.commit() 
    except sqlite3.IntegrityError:
        raise HTTPException (
        status_code=400,
        detail='email already exists') 
    return {'Message':'Signup successfully 🎉'}
@app.post('/login')
async def signin(data: OAuth2PasswordRequestForm=Depends()):
   cursor.execute(
   'SELECT * FROM users WHERE EMAIL=?', [data.username]
   )
   user=cursor.fetchone()
   if not user:
       raise HTTPException(
       status_code=401,
       detail='invalid credentials')
   if not await run_in_threadpool(
    bcrypt.checkpw,
       data.password.encode(), 
        user['password'].encode()): 
           raise HTTPException(
           status_code=401,
           detail='invalid credentials') 
   token=create_token(user) 
   return {'token': token,
                 'token_type':'bearer',
                'message': 'login successfully'}
                
@app.post('/post')
async def post_news(data: News, user=Depends (get_user)): 
     if user['role'] !='admin':
        raise HTTPException (
        status_code=403,
        detail='You are not allowed to use this feature' 
        ) 
  
     cursor.execute(
    'INSERT INTO news (date,title, content) VALUES (?,?,?)', [data.date, data.title, data.content]
    )
     conn.commit( )
     return {'message':'News posted successfully 🎉'} 
    
    
    
@app.get('/read')
async def read_news(user=Depends(get_user)): 
 
   
    cursor.execute(
    'SELECT * FROM news')
    posts=cursor.fetchall()
    if not posts:
        raise HTTPException(
        status_code=404,
        detail='No news posted yet'
        ) 
    return [dict(post) for post in posts]
        
    
@app.get('/posts/{post_title}')
async def search_news(post_title:str, user=Depends(get_user)):
    cursor.execute(
    'SELECT * FROM news WHERE TITLE like ?', [f'%{post_title}%'] 
    ) 
    found=cursor.fetchall()
    if not found:
        raise HTTPException (
        status_code=404,
        detail='news not found, make sure you search by title') 
    return [dict(news) for news in found]
    
    
                
