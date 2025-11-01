from backend.app import app, db
from backend.app import app
from backend.database import db

with app.app_context():
    db.create_all()
    print("Database initialized.")
