from .database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_timestamp = db.Column(db.DateTime, server_default=db.func.now())
    axioms = db.relationship('Axiom', backref='user', lazy=True)

class Axiom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
