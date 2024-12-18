from fastapi import FastAPI, Depends
import sqlalchemy as sql


from app.database.connection import session, get_connection
from app.config import settings

from app.database.models import Movie



app = FastAPI()



@app.get('/{id}')
async def get_movie_info(id: int, db: sql.orm.Session = Depends(get_connection)):
    statement = sql.select(Movie).filter_by(id=id)
    return db.execute(statement).scalars().all()

