try:
    import app.database.populate
except Exception as e:
    print(f'Could not populate a database: {e}')