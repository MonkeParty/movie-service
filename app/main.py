from fastapi import FastAPI, Depends
import sqlalchemy as sql


from app.database.connection import session, get_connection
from app.config import settings



app = FastAPI()
