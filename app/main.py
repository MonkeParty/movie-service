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
    statement = sql.select(Movie).filter_by(id=id)
    return db.execute(statement).scalars().all()

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
        existing_rating.timestamp = datetime.now()
    else:
        new_rating = Rating(
            user_id=user_id,
            movie_id=id,
            rating=rating,
            timestamp=datetime.now()
        )
        db.add(new_rating)

    db.commit()
