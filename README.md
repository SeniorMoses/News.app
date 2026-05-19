HiveNews API

Simple news API built with FastAPI, JWT authentication, and SQLite.

I Built and deployed from a phone using Python and Render.

Features

User signup and login

Password hashing with bcrypt

JWT authentication

Protected routes

Role-based access (admin and user)

Create and read news posts

Search news by title

SQLite database

CORS enabled for frontend connection
Deployed on Render


Endpoints

GET	/	Server status
POST	/signup	Register user
POST	/login	Login user
POST	/post	Post news (admin only)
GET	/read	Read all news
GET	/posts/{post_title}	Search news by title


Authentication

This API uses Bearer Token authentication.

Environment Variables

Create a .env file and add:

SECRET →SECRET

DBURL → DBURL


Run Locally

1. Clone or download the project


2. Install the required packages


3. Create a .env file and add your secret key and database name


4. Start the FastAPI server


5. Open the local server URL in your browser or API testing tool



Deployment

Deployed on Render.

Notes

This project was built while learning backend development with FastAPI.
Started learning Python less than 2 months ago and built the project mainly from a phone.# News.app
