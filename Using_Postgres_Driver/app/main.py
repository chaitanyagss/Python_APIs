from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

try:
    conn = psycopg2.connect(host = 'localhost', database = 'fastapidb', user='postgres', port=5433, password = '', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print('Connection established')
except Exception as e:
    print('Could not connect to fastapi database: ', e)
    time.sleep(3)

app = FastAPI()

my_posts = [{"title": "title 1", "content": "content 1", "id": 1},{"title": "title 2", "content": "content 2", "id": 2}  ]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p 

@app.get("/")
async def root():
    return {"message": "Hello!"}

@app.get("/posts")
def get_posts():
    cursor.execute('''SELECT * FROM posts''')
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute('''INSERT INTO posts(title, content, published) VALUES (%s, %s, %s) RETURNING *''', (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute('''SELECT * FROM posts where id = %s''', (str(id),) )
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Post with ID-{id} not found")
    print(post)
    return {"data": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute('''DELETE from posts where id = %s RETURNING *''', (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Post with ID-{id} not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_post(id: int, post: Post):
    cursor.execute('''UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s returning *''', (post.title, post.content, post.published, str(id),))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Post with ID-{id} not found")
    return {'data': updated_post}