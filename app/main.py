from datetime import datetime


from fastapi import FastAPI, Depends, Form, status
from pydantic import BaseModel, Field
import sqlalchemy as sql


from app.auth.auth import get_current_user_id
from app.database.connection import session, get_connection
from app.config import settings

from app.database.models import *



app = FastAPI()



@app.get('/{id}')
async def get_movie_info(id: int, db: sql.orm.Session = Depends(get_connection)):
    return db.execute(sql.select(Movie).filter_by(id=id)).scalars().all()

@app.get('/?category={category_name}')
async def get_movie_with_category(category_name: str):
    return status.HTTP_501_NOT_IMPLEMENTED


@app.post('/{id}/rate', status_code=status.HTTP_200_OK)
async def rate_movie(
    id: int,
    rating: int = Form(..., ge=1, le=10),
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection)
):
    existing_rating_query = db.query(Rating).filter_by(user_id=user_id, movie_id=id)
    existing_rating = existing_rating_query.first()

    if existing_rating:
        existing_rating.rating = rating
        existing_rating.time = datetime.now()
    else:
        db.add(Rating(
            user_id=user_id,
            movie_id=id,
            rating=rating,
            time=datetime.now()
        ))

    db.commit()

@app.post('/{id}/comment', status_code=status.HTTP_200_OK)
async def make_comment(
    id: int,
    text: str = Form(...),
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection)
):
    existing_comment_query = db.query(Comment).filter_by(user_id=user_id, movie_id=id)
    existing_comment = existing_comment_query.first()

    if existing_comment:
        existing_comment.text = text
        existing_comment.time = datetime.now()
    else:
        db.add(Comment(
            user_id=user_id,
            movie_id=id,
            text=text,
            time=datetime.now()
        ))

    db.commit()

@app.delete('/{id}/comment', status_code=status.HTTP_200_OK)
async def delete_comment(
    id: int,
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection)
):
    db.execute(sql.delete(Comment).filter_by(user_id=user_id, movie_id=id))

    db.commit()
