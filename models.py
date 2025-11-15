from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Enum
from constants import (
    ITEM_FIELD_NAME,
    ITEM_FIELD_QUANTITY,
    ITEM_FIELD_TAGS,
    ITEM_FIELD_LOCATION_ID,
    ITEM_FIELD_EXPIRES,
    ITEM_FIELD_UPDATED_BY,
    LOCATION_ID,
    LOCATION_NAME,
    TAG_ID,
    TAG_NAME,
    UserRole,
)

db = SQLAlchemy()

# clean this up later
item_tags = db.Table(
    "item_tags",
    db.Column("item_id", db.Integer, db.ForeignKey("item.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)

camera_gear_tags = db.Table(
    "camera_gear_tags",
    db.Column(
        "camera_gear_id", db.Integer, db.ForeignKey("camera_gear.id"), primary_key=True
    ),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)

lab_equipment_tags = db.Table(
    "lab_equipment_tags",
    db.Column(
        "lab_equipment_id",
        db.Integer,
        db.ForeignKey("lab_equipment.id"),
        primary_key=True,
    ),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


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


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    tags = db.relationship("Tag", secondary="item_tags", backref="items")
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    expires = db.Column(db.Date, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Item {self.name}>"

    # relationship to Location so templates and views can use `item.location`
    location = db.relationship("Location", backref="items", foreign_keys=[location_id])

    # optional convenience relationship to the User who last updated the item
    updated_by_user = db.relationship(
        "User", foreign_keys=[updated_by], backref="updated_items", uselist=False
    )

    def to_dict(self):
        """Return a serializable dict for this Item using the shared item field constants.
        Tags are returned as a list of names. `location_id` uses the constant key:
        the human-readable `location` name is provided under the key 'location'.
        """
        tags = [t.name for t in getattr(self, "tags", [])]
        location_name = None
        try:
            if getattr(self, "location", None):
                location_name = self.location.name
        except Exception:
            location_name = None

        updater = None
        try:
            if self.updated_by:
                # prefer the relationship when available
                if getattr(self, "updated_by_user", None):
                    updater = self.updated_by_user.email
                else:
                    updater = self.updated_by
        except Exception:
            updater = None

        return {
            "id": self.id,
            ITEM_FIELD_NAME: self.name,
            ITEM_FIELD_QUANTITY: self.quantity,
            ITEM_FIELD_TAGS: tags,
            ITEM_FIELD_LOCATION_ID: self.location_id,
            "location": location_name,
            ITEM_FIELD_EXPIRES: self.expires.isoformat() if self.expires else None,
            "last_updated": (
                self.last_updated.isoformat() if self.last_updated else None
            ),
            ITEM_FIELD_UPDATED_BY: updater,
        }


class CameraGear(db.Model):
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


class LabEquipment(db.Model):
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
