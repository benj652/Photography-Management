from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

item_tags = db.Table(
    'item_tags',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture = db.Column(db.String(200))
    def __repr__(self):
        return f'<User {self.email}>'
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "profile_picture": self.profile_picture,
        }

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

    # relationship to Location so templates and views can use `item.location`
    location = db.relationship('Location', backref='items', foreign_keys=[location_id])

    # optional convenience relationship to the User who last updated the item
    updated_by_user = db.relationship('User', foreign_keys=[updated_by], backref='updated_items', uselist=False)

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
