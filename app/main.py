from typing import Optional

from fastapi import Body, Depends, FastAPI, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from fastapi.exceptions import HTTPException

from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)


class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None


app = FastAPI()


@app.get("/posts", status_code=status.HTTP_200_OK)
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/posts/{id}", status_code=status.HTTP_200_OK)
async def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist",
        )
    return {"data": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist",
        )
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.patch("/posts/{id}", status_code=status.HTTP_200_OK)
def patch_post(id: int, post=Post, db=Depends(get_db)):
    query = db.query(models.Post).filter(models.Post.id == id)
    old_post = query.first()
    if old_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist",
        )
    query.update(post.dict(), synchronize_session=False)
    db.commit()
    return {"data": query.first()}
