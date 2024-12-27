from sqlalchemy import Column, Index, Integer, String, Float, Time, ForeignKey, DateTime, func

from app.database.connection import Base


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)

class Rating(Base):
    __tablename__ = 'ratings'

    user_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    rating = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    __table_args__ = (Index('ix_genres_name_lower', func.lower(name), unique=True),)

class MovieGenre(Base):
    __tablename__ = 'movie_genres'

    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.id'), primary_key=True)

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    __table_args__ = (Index('ix_tags_name_lower', func.lower(name), unique=True),)

class MovieTag(Base):
    __tablename__ = 'movie_tags'

    user_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    relevance = Column(Float)

class Comment(Base):
    __tablename__ = 'comments'

    user_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    text = Column(String, nullable=False)
    time = Column(DateTime, nullable=False)
