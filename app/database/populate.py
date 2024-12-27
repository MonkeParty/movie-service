from datetime import datetime
from app.database.models import Base, Movie, Rating, Genre, MovieGenre, Tag, MovieTag
from app.database import connection


def populate_database():
    session = connection.session()

    try:
        genres = ['action', 'comedy', 'drama', 'horror', 'sci-fi']
        session.add_all([Genre(name=genre) for genre in genres])

        tags = ['classic', 'funny', 'suspense', 'thriller', 'romantic']
        session.add_all([Tag(name=tag) for tag in tags])

        movies = [
            {'title': 'The Matrix'},
            {'title': 'Inception'},
            {'title': 'The Godfather'}
        ]
        session.add_all([Movie(title=movie['title']) for movie in movies])
        session.flush() # flush to get ids for Movies

        # add ratings
        ratings = [
            {'user_id': 1, 'movie_id': 1, 'rating': 5.0, 'time': datetime.now()},
            {'user_id': 2, 'movie_id': 2, 'rating': 4.5, 'time': datetime.now()},
            {'user_id': 3, 'movie_id': 3, 'rating': 4.8, 'time': datetime.now()}
        ]
        session.add_all([Rating(**rating) for rating in ratings])

        movie_genres = [
            {'movie_id': 1, 'genre_id': 5}, # The Matrix is Sci-Fi
            {'movie_id': 2, 'genre_id': 1}, # Inception is Action
            {'movie_id': 3, 'genre_id': 3}  # The Godfather is Drama
        ]
        session.add_all([MovieGenre(**movie_genre) for movie_genre in movie_genres])

        movie_tags = [
            {'user_id': 1, 'movie_id': 1, 'tag_id': 1, 'relevance': 0.9}, # User 1 tagged The Matrix as 'Classic'
            {'user_id': 2, 'movie_id': 2, 'tag_id': 4, 'relevance': 0.5}, # User 2 tagged Inception as 'Thriller'
            {'user_id': 3, 'movie_id': 3, 'tag_id': 5, 'relevance': 0.2}  # User 3 tagged The Godfather as 'Romantic'
        ]
        session.add_all([MovieTag(**movie_tag) for movie_tag in movie_tags])

        session.commit()
        print('Database populated successfully!')

    except Exception as e:
        print(f'Error populating database: {e}')
        session.rollback()

    finally:
        session.close()

Base.metadata.drop_all(bind=connection.engine)
Base.metadata.create_all(bind=connection.engine)

populate_database()
