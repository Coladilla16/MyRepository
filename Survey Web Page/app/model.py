from flask_login import UserMixin
from . import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    surveys = db.relationship('Survey', backref='creator', lazy=False, cascade='all, delete',
                              order_by='desc(Survey.date_created)')
