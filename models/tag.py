from .base import db
from constants import TAG_ID, TAG_NAME


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Tag {self.name}>"

    def to_dict(self):
        return {
            TAG_ID: self.id,
            TAG_NAME: self.name,
        }