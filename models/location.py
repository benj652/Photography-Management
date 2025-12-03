"""Location model for storing human-readable locations.

Provides the Location SQLAlchemy model used by items and gear.
"""

from constants import LOCATION_ID, LOCATION_NAME
from .base import db


class Location(db.Model):
    """Simple location record used by items and gear."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        """Return a readable representation for debugging."""
        return f"<Location {self.name}>"

    def to_dict(self):
        """Return a simple dict representation of the location."""
        return {
            LOCATION_ID: self.id,
            LOCATION_NAME: self.name,
        }
