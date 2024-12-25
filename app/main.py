from datetime import datetime


from fastapi import FastAPI, Depends, Form, Response, status
from pydantic import BaseModel
import sqlalchemy as sql


from app.auth.auth import get_current_user_id, user_is_admin
from app.database.connection import get_connection

from app.database.models import *



app = FastAPI()



@app.get('/{id}')
async def get_movie_info(id: int, db: sql.orm.Session = Depends(get_connection)):
    return db.execute(sql.select(Movie).filter_by(id=id)).scalars().all()

@app.get('/?category={category_name}')
async def get_movie_with_category(
    response: Response,
    category_name: str
):
    response.status_code = status.HTTP_501_NOT_IMPLEMENTED


@app.post('/{id}/rate')
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

@app.post('/{id}/comment')
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

@app.delete('/{id}/comment')
async def delete_comment(
    id: int,
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection)
):
    db.execute(sql.delete(Comment).filter_by(user_id=user_id, movie_id=id))
    db.commit()


class Metadata(BaseModel):
    title: str
    genres: list[dict[str, str]]

@app.post('/')
async def upload_a_movie(
    response: Response,
    metadata: Metadata,
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection),
):
    if not user_is_admin(user_id):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    movie_data = {'title': metadata.title}

    movie = Movie(**movie_data)

    try:
        db.add(movie)
        db.commit()
        db.refresh(movie)

        genre_names = [genre['name'].lower() for genre in metadata.genres]

        existing_genres = db.query(Genre).filter(Genre.name.in_(genre_names)).all()
        existing_genre_names = {genre.name for genre in existing_genres}

        new_genres = [
            Genre(name=name)
            for name in genre_names
            if name not in existing_genre_names
        ]

        db.bulk_save_objects(new_genres)
        db.commit()

        all_genres = db.query(Genre).filter(Genre.name.in_(genre_names)).all()

        genre_id_map = {genre.name: genre.id for genre in all_genres}

        movie_genres = [
            MovieGenre(movie_id=movie.id, genre_id=genre_id_map[name])
            for name in genre_names
        ]
        db.bulk_save_objects(movie_genres)
        db.commit()

        return {
            'id': movie.id
        }
    except Exception as e:
        db.rollback()
        response.status_code = 500

        return {
            'error': 'Internal Server Error'
        }



# TODO
@app.put('/', status_code=status.HTTP_401_UNAUTHORIZED)
async def update_a_movie(
    response: Response,
    metadata: Metadata,
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection),
):
    response.status_code = status.HTTP_501_NOT_IMPLEMENTED


@app.delete('/{id}')
async def delete_a_movie(
    response: Response,
    id: int,
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection),
):
    if not user_is_admin(user_id):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    db.execute(sql.delete(MovieGenre).filter_by(movie_id=id))
    db.execute(sql.delete(MovieTag).filter_by(movie_id=id))
    db.execute(sql.delete(Rating).filter_by(movie_id=id))
    db.execute(sql.delete(Movie).filter_by(id=id))

    db.commit()