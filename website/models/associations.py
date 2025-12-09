"""Association tables for many-to-many relationships.

This module defines the association tables that SQLAlchemy uses to manage
many-to-many relationships between items and tags.
"""

from website import db

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
