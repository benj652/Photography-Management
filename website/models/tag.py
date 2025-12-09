"""Tag model for categorizing inventory items.

This file defines the Tag model which serves as categories/labels for
CameraGear, LabEquipment, and Consumables.
"""

from website import db
from ..constants import TAG_ID, TAG_NAME


class Tag(db.Model):
    """Tag used to categorize items and equipment."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        """Readable representation for the Tag object."""
        return f"<Tag {self.name}>"

    def to_dict(self):
        """Return a serializable dict for this Tag instance."""
        return {
            TAG_ID: self.id,
            TAG_NAME: self.name,
        }
