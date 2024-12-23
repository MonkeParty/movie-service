from sqlalchemy import Column, Integer, String, Float, Time, ForeignKey

from .connection import Base


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)

class Rating(Base):
    __tablename__ = 'ratings'

    user_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    rating = Column(Float, nullable=False)
    timestamp = Column(Time, nullable=False)

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

class MovieGenre(Base):
    __tablename__ = 'movie_genres'

    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.id'), primary_key=True)

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

class MovieTag(Base):
    __tablename__ = 'movie_tags'

    user_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)