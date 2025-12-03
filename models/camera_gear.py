"""Camera gear model and convenience helpers.

Defines the CameraGear SQLAlchemy model and helper methods such as
``to_dict`` for API serialization.
"""

from constants import (
    ITEM_FIELD_NAME,
    ITEM_FIELD_TAGS,
    ITEM_FIELD_LOCATION_ID,
    ITEM_FIELD_UPDATED_BY,
)
from .base import db


class CameraGear(db.Model):
    """Represents a camera gear item stored in inventory."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tags = db.relationship("Tag", secondary="camera_gear_tags", backref="camera_gear")
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    last_updated = db.Column(db.DateTime, nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Checkout tracking fields
    is_checked_out = db.Column(db.Boolean, default=False, nullable=False)
    checked_out_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    checked_out_date = db.Column(db.DateTime, nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<CameraGear {self.name}>"

    # relationship to Location so templates and views can use `camera_gear.location`
    location = db.relationship(
        "Location", backref="camera_gear", foreign_keys=[location_id]
    )

    updated_by_user = db.relationship(
        "User", foreign_keys=[updated_by], backref="updated_camera_gear", uselist=False
    )
    checked_out_by_user = db.relationship(
        "User",
        foreign_keys=[checked_out_by],
        backref="checked_out_camera_gear",
        uselist=False,
    )

    def to_dict(self):
        """Return a serializable dict for this CameraGear instance."""
        tags = [t.name for t in getattr(self, "tags", [])]

        # Get location name
        location_name = None
        try:
            if getattr(self, "location", None):
                location_name = self.location.name
        except Exception:
            location_name = None

        updater = None
        checked_out_user = None
        try:
            if self.updated_by and getattr(self, "updated_by_user", None):
                updater = self.updated_by_user.email
            if self.checked_out_by and getattr(self, "checked_out_by_user", None):
                checked_out_user = self.checked_out_by_user.email
        except Exception:
            pass

        return {
            "id": self.id,
            ITEM_FIELD_NAME: self.name,
            ITEM_FIELD_TAGS: tags,
            ITEM_FIELD_LOCATION_ID: self.location_id,
            "location": location_name,
            "last_updated": (
                self.last_updated.isoformat() if self.last_updated else None
            ),
            ITEM_FIELD_UPDATED_BY: updater,
            "is_checked_out": self.is_checked_out,
            "checked_out_by": checked_out_user,
            "checked_out_date": (
                self.checked_out_date.isoformat() if self.checked_out_date else None
            ),
            "return_date": self.return_date.isoformat() if self.return_date else None,
        }
