from constants import LOCATION_ID, LOCATION_NAME
from .base import db


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Location {self.name}>"

    def to_dict(self):
        return {
            LOCATION_ID: self.id,
            LOCATION_NAME: self.name,
        }
