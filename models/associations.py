"""Association tables used by many-to-many relationships for models.

This module defines SQLAlchemy Table objects that are used to relate
items, tags and other models.
"""

from .base import db
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

consumable_tags = db.Table(
    "consumable_tags",
    db.Column(
        "consumable_id", db.Integer, db.ForeignKey("consumable.id"), primary_key=True
    ),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)
