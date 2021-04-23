from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256))
    role = db.Column(db.String(100))


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(200))
    uploaded_by = db.Column(db.String(200))
    assigned_to = db.Column(db.String(200))
    date = db.Column(db.String(255), default=lambda: date.today())


class Advise:
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), unique=True)
    advise = db.Column(db.String(5000))
    given_by = db.Column(db.String(200))
    given_to = db.Column(db.String(200))
