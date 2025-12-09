"""Location model for tracking where items are stored.

This file defines the Location model which represents physical locations
where inventory items can be stored.
"""

from website import db


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
            "id": self.id,
            "name": self.name,
        }
