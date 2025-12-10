"""Lab equipment model definitions and helpers.

Defines LabEquipment model and common serialization helpers.
"""

from ..constants import (
    ITEM_FIELD_NAME,
    ITEM_FIELD_TAGS,
    ITEM_FIELD_UPDATED_BY,
)

from website import db

class LabEquipment(db.Model):
    """Represents lab equipment that can be tracked and serviced."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tags = db.relationship(
        "Tag", secondary="lab_equipment_tags", backref="lab_equipment"
    )
    last_updated = db.Column(db.DateTime, nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Service tracking fields
    last_serviced_on = db.Column(db.Date, nullable=True)
    last_serviced_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    service_frequency = db.Column(
        db.String(100), nullable=True
    )  # e.g., "monthly", "yearly", etc.

    def __repr__(self):
        """Return a readable representation for debugging."""
        return f"<LabEquipment {self.name}>"

    updated_by_user = db.relationship(
        "User",
        foreign_keys=[updated_by],
        backref="updated_lab_equipment",
        uselist=False,
    )
    last_serviced_by_user = db.relationship(
        "User",
        foreign_keys=[last_serviced_by],
        backref="serviced_lab_equipment",
        uselist=False,
    )

    def to_dict(self):
        """Return a serializable dict for this LabEquipment instance."""
        tags = [t.name for t in getattr(self, "tags", [])]

        updater = None
        serviced_by_user = None
        try:
            if self.updated_by and getattr(self, "updated_by_user", None):
                updater = self.updated_by_user.email
            if self.last_serviced_by and getattr(self, "last_serviced_by_user", None):
                serviced_by_user = self.last_serviced_by_user.email
        except Exception:
            pass

        return {
            "id": self.id,
            ITEM_FIELD_NAME: self.name,
            ITEM_FIELD_TAGS: tags,
            "last_updated": (
                self.last_updated.isoformat() if self.last_updated else None
            ),
            ITEM_FIELD_UPDATED_BY: updater,
            "last_serviced_on": (
                self.last_serviced_on.isoformat() if self.last_serviced_on else None
            ),
            "last_serviced_by": serviced_by_user,
            "service_frequency": self.service_frequency,
        }
