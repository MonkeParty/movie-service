#!/bin/sh
python3 app/database/populate.py &&
uvicorn app.main:app --reload --host ${HOST} --port ${PORT} --proxy-headers
