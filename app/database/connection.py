from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(f'postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}', echo=True)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_connection():
    connection = session()

    try:
        yield connection
    finally:
        connection.close()