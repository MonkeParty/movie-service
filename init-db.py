from pathlib import Path

from sqlalchemy import inspect
import pandas as pd

from app.database.connection import Base, engine
from app.database.models import *


def is_database_initialized():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return 'movies' in tables

def populate_with_csv():
    # TODO: do something about it
    # commented out csvs are HUGE

    movies = pd.read_csv(Path.cwd()/'initial-db'/'movie.csv')
    # ratings = pd.read_csv(Path.cwd()/'initial-db'/'rating.csv')
    links = pd.read_csv(Path.cwd()/'initial-db'/'link.csv')
    tags = pd.read_csv(Path.cwd()/'initial-db'/'tag.csv')
    genome_tags = pd.read_csv(Path.cwd()/'initial-db'/'genome_tags.csv')
    # genome_scores = pd.read_csv(Path.cwd()/'initial-db'/'genome_scores.csv')

    movies.rename(columns={'movieId': 'id'})
    # ratings.rename(columns={'userId': 'user_id', 'movieId': 'movie_id'})
    links.rename(columns={'movieId': 'movie_id', 'imdbId': 'imdb_id', 'tmdbId': 'tmdb_id'})
    tags.rename(columns={'userId': 'user_id', 'movieId': 'movie_id'})
    genome_tags.rename(columns={'tagId': 'id'})
    # genome_scores.rename(columns={'movieId': 'movie_id', 'tagId': 'tag_id'})

    movies.to_sql(name=Movie.__tablename__, con=engine)
    # ratings.to_sql(name=Rating.__tablename__, con=engine)
    links.to_sql(name=Link.__tablename__, con=engine)
    tags.to_sql(name=Tag.__tablename__, con=engine)
    genome_tags.to_sql(name=GenomeTag.__tablename__, con=engine)
    # genome_scores.to_sql(name=GenomeScore.__tablename__, con=engine)


def initialize_database():
    if is_database_initialized():
        Base.metadata.drop_all(bind=engine)
    populate_with_csv()

initialize_database()