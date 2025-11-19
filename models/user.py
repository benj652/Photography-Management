from flask_login import UserMixin
from sqlalchemy import Enum
from .base import db
from constants import UserRole


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture = db.Column(db.String(200))
    role = db.Column(Enum(UserRole), nullable=False)

    def __repr__(self):
        return f"<User {self.email} Role {self.role}>"

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "role": self.role.value if self.role else None,
        }

    def save(self):
        """Save the user to the database"""
        db.session.add(self)
        db.session.commit()