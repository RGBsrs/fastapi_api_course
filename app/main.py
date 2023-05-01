from typing import Optional

from fastapi import Body, Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)


class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/posts")
async def create_post(post: Post = Body(...)):
    return post


@app.get("/sql-alc")
def test_posts(db: Session = Depends(get_db)):
    return {"status": "success"}
