"""Model package exports.

Re-export SQLAlchemy `db` and model classes for convenient imports
from the top-level `models` package.
"""

from .base import db
from .user import User
from .camera_gear import CameraGear
from .lab_equipment import LabEquipment
from .consumables import Consumable
from .location import Location
from .tag import Tag
from .associations import (
    item_tags,
    camera_gear_tags,
    lab_equipment_tags,
    consumable_tags,
)

__all__ = [
    'db',
    'User',
    'CameraGear',
    'LabEquipment',
    'Consumable',
    'Location',
    'Tag',
    'item_tags',
    'camera_gear_tags',
    'lab_equipment_tags',
    'consumable_tags',
]
