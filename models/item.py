from .base import db
from constants import (
    ITEM_FIELD_NAME,
    ITEM_FIELD_QUANTITY,
    ITEM_FIELD_TAGS,
    ITEM_FIELD_LOCATION_ID,
    ITEM_FIELD_EXPIRES,
    ITEM_FIELD_UPDATED_BY,
)


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