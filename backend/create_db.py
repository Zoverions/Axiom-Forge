from backend.app import app, db
from backend.models import User, Axiom

with app.app_context():
    db.create_all()
    print("Database initialized.")
