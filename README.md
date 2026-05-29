

Hivenews is a simple News app where users can read and explore news posted Admins have access to all the endpoints including news and only users with the admin role can post news.

Features of HiveNews

Authentication used for secured login session and role based access control 

Endpoints:

- Signup / user register to the app with username, email, password, email is verified if email is duplicate it rejects the signup and recommends login username must be at least 3 characters password must be at least 8 characters password is hashed using bcrypt before it touches the database

- Login / user log in User provide email and password Login compares details given with database records if the the details given is accurate, it will login the user, else login will reject with "invalid credentials" as the returning message then token is generated

- Post_news / this endpoints is only reserved for users with the "admin" role if user has the regular "user", they are forbidden to use this feature

- Read_news/ this feature is for all users its for exploring all news recorded in the database

- Search_news / this endpoint is for searching news with title, it uses the "like (%) " operator to match incompleted search

Database: i used postgreSQL there is the users table and the news table

How to run this app is live on render url :
https://hivenews-ixfx.onrender.com/docs

How to run locally

1. Clone the repo
2. Create a .env file with DBURL and SECRET
3. Run pip install -r requirements.txt
4. Run uvicorn HiveNews:app --reload
5. Open http://localhost:8000/docs
