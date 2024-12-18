from sqlalchemy import Column, Integer, String, Float, Time, ForeignKey

from .connection import Base


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genres = Column(String, nullable=False)

class Rating(Base):
    __tablename__ = 'ratings'

    user_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    rating = Column(Float, nullable=False)
    timestamp = Column(Time, nullable=False)

class Link(Base):
    __tablename__ = 'links'

    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    imdb_id = Column(Integer)
    tmdb_id = Column(Integer)

class Tag(Base):
    __tablename__ = 'tags'

    user_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    tag = Column(String, primary_key=True)
    timestamp = Column(Time, nullable=False, primary_key=True)


class GenomeTag(Base):
    __tablename__ = 'genome_tags'

    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False)

class GenomeScore(Base):
    __tablename__ = 'genome_scores'

    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('genome_tags.id'))
    relevance = Column(Float, nullable=False)
