from typing import List
from fastapi import Depends, FastAPI, Response, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from fastapi.exceptions import HTTPException

from . import models, schemas
from .database import engine, get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get(
    "/posts", status_code=status.HTTP_200_OK, response_model=List[schemas.PostResponse]
)
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.post(
    "/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get(
    "/posts/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse
)
async def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist",
        )
    return post


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


@app.patch(
    "/posts/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse
)
def patch_post(id: int, post=schemas.PostCreate, db=Depends(get_db)):
    query = db.query(models.Post).filter(models.Post.id == id)
    old_post = query.first()
    if old_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist",
        )
    query.update(post.dict(), synchronize_session=False)
    db.commit()
    return query.first()


@app.post(
    "/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse
)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pwd = pwd_context.hash(user.password)
    user.password = hashed_pwd
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
