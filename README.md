# movie-service

# How to run

```sh
docker compose up -d
uvicorn app.main:app --reload
```

## Initializing the database
```sh
python3 populate.py
```