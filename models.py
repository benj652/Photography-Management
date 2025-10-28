from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=True, nullable=False)
    last_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture = db.Column(db.String(200))
    def __repr__(self):
        return f'<User {self.email}>'

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    tags = db.relationship('Tag', secondary='item_tags', backref='items')
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    expires = db.Column(db.Date, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return f'<Item {self.name}>'

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    def __repr__(self):
        return f'<Location {self.name}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    def __repr__(self):
        return f'<Tag {self.name}>'
