"""Notes model for adding contextual information to inventory items.

This file defines the Note model which allows users to add timestamped
notes to any inventory item for tracking maintenance, issues, etc.
"""

from website import db
from datetime import datetime


class Note(db.Model):
    """Represents a note that can be attached to inventory items."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)

    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    # Foreign keys to different item types (only one should be set per note)
    camera_gear_id = db.Column(db.Integer, db.ForeignKey("camera_gear.id"), unique=True, nullable=True)
    lab_equipment_id = db.Column(db.Integer, db.ForeignKey("lab_equipment.id"), unique=True, nullable=True)
    consumable_id = db.Column(db.Integer, db.ForeignKey("consumable.id"), unique=True, nullable=True)

    # Relationships to items
    camera_gear = db.relationship(
        "CameraGear", backref=db.backref("note", uselist=False, cascade="all, delete")
    )
    lab_equipment = db.relationship(
        "LabEquipment", backref=db.backref("note", uselist=False, cascade="all, delete")
    )
    consumable = db.relationship(
        "Consumable", backref=db.backref("note", uselist=False, cascade="all, delete")
    )

    # Relationships to users
    created_by_user = db.relationship(
        "User", foreign_keys=[created_by], backref="created_notes", uselist=False
    )
    updated_by_user = db.relationship(
        "User", foreign_keys=[updated_by], backref="updated_notes", uselist=False
    )

    def __repr__(self):
        """Return a readable representation for debugging."""
        return f"<Note {self.id}>"

    def to_dict(self):
        """Return a serializable dict for this Note instance."""
        creator = None
        updater = None
        try:
            if self.created_by and getattr(self, "created_by_user", None):
                creator = self.created_by_user.email
            if self.updated_by and getattr(self, "updated_by_user", None):
                updater = self.updated_by_user.email
        except Exception:
            pass

        # Determine which item this note is attached to
        item_type = None
        item_id = None
        item_name = None

        try:
            if self.camera_gear_id and getattr(self, "camera_gear", None):
                item_type = "camera_gear"
                item_id = self.camera_gear_id
                item_name = self.camera_gear.name if self.camera_gear else None
            elif self.lab_equipment_id and getattr(self, "lab_equipment", None):
                item_type = "lab_equipment"
                item_id = self.lab_equipment_id
                item_name = self.lab_equipment.name if self.lab_equipment else None
            elif self.consumable_id and getattr(self, "consumable", None):
                item_type = "consumable"
                item_id = self.consumable_id
                item_name = self.consumable.name if self.consumable else None
        except Exception:
            pass

        # Format timestamps as UTC ISO strings with 'Z' suffix
        created_at_str = None
        updated_at_str = None
        if self.created_at:
            created_at_str = self.created_at.isoformat() + 'Z' if self.created_at.tzinfo is None else self.created_at.isoformat()
        if self.updated_at:
            updated_at_str = self.updated_at.isoformat() + 'Z' if self.updated_at.tzinfo is None else self.updated_at.isoformat()

        return {
            "id": self.id,
            "content": self.content,
            "created_at": created_at_str,
            "updated_at": updated_at_str,
            "created_by": creator,
            "updated_by": updater,
            "item_type": item_type,
            "item_id": item_id,
            "item_name": item_name,
        }
