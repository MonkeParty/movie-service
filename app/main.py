from datetime import datetime


from fastapi import FastAPI, Depends, Form, HTTPException, Response, status
from kafka import KafkaProducer
from pydantic import BaseModel
import sqlalchemy as sql
import json


from app.auth.auth import can_user_action_on_movie, get_current_user_id, user_is_admin
from app.database.connection import get_connection

from app.database.models import *
from app.events.writer import KafkaEventWriter
from app.events.events import Event, EventType

from app.config import settings



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



event_writer = KafkaEventWriter(
    topic=settings.event_bus_topic_name,
    kafka_producer=KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_server,
    )
)

@app.post('/{id}/rate')
async def rate_movie(
    response: Response,
    id: int,
    rating: int = Form(..., ge=1, le=5),
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection)
):
    if not can_user_action_on_movie(user_id, 'rate', id):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

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

    genres = db.query(Genre.name).join(MovieGenre).filter(MovieGenre.movie_id == id).all()
    genres = [genre.name for genre in genres]

    tags = db.query(Tag.name).join(MovieTag).filter(MovieTag.movie_id == id).all()
    tags = [tag.name for tag in tags]

    event_writer.send_event(Event(
        EventType.MovieRated,
        json.dumps({
            'user_id': user_id,
            'movie_id': id,
            'genres': genres,
            'tags': tags,
            'rating': rating,
        })
    ))

    db.commit()


class TagRequest(BaseModel):
    name: str
    relevance: float = Form(..., ge=0.1, le=1.0)

@app.post('/{id}/tag')
async def tag_movie(
    response: Response,
    id: int,
    tag: TagRequest,
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection)
):
    if not can_user_action_on_movie(user_id, 'rate', id):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    try:
        db_tag = db.query(Tag).filter_by(name=tag.name.lower()).one_or_none()
        if not db_tag:
            db_tag = Tag(name=tag.name)
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)

        movie_tag = db.query(MovieTag).filter_by(
            user_id=user_id,
            movie_id=id,
            tag_id=db_tag.id
        ).one_or_none()

        if not movie_tag: # create new movie tag
            movie_tag = MovieTag(
                user_id=user_id,
                movie_id=id,
                tag_id=db_tag.id,
                relevance=tag.relevance
            )
            db.add(movie_tag)
        else: # update the already set one
            movie_tag.relevance = tag.relevance

        db.commit()
        return {
            'msg': 'Tag added successfully'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Internal server error: {str(e)}')

    db.commit()


@app.post('/{id}/comment')
async def make_comment(
    response: Response,
    id: int,
    text: str,
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection)
):
    if not can_user_action_on_movie(user_id, 'comment', id):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

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
    response: Response,
    id: int,
    user_id: int = Depends(get_current_user_id),
    db: sql.orm.Session = Depends(get_connection)
):
    if not can_user_action_on_movie(user_id, 'comment', id):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    db.execute(sql.delete(Comment).filter_by(user_id=user_id, movie_id=id))
    db.commit()


class Metadata(BaseModel):
    title: str
    genres: list[dict[str, str]]
    is_free: bool

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

        if metadata.is_free:
            event_writer.send_event(Event(
                EventType.SetMovieFree,
                movie.id,
            ))

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
