"""Unit tests for the Tag model and its methods.

Tests focus on the to_dict() and __repr__() methods.
"""

# pylint: disable=missing-module-docstring,import-error,line-too-long,
# pylint: disable=missing-function-docstring,missing-class-docstring,unused-import
# pylint: disable=redefined-outer-name

import pytest

from models import Tag, db
from constants import TAG_ID, TAG_NAME


@pytest.fixture
def sample_tag(app_ctx):
    """Create and return a sample tag."""
    tag = Tag(name="Test Tag")
    db.session.add(tag)
    db.session.commit()
    return tag


class TestTagToDict:
    """Test Tag.to_dict() method."""

    def test_to_dict_returns_correct_structure(self, app_ctx, sample_tag):
        """Test to_dict returns correct dictionary structure."""
        result = sample_tag.to_dict()
        assert TAG_ID in result
        assert TAG_NAME in result
        assert result[TAG_ID] == sample_tag.id
        assert result[TAG_NAME] == sample_tag.name

    def test_to_dict_with_different_name(self, app_ctx):
        """Test to_dict with different tag name."""
        tag = Tag(name="Photography")
        db.session.add(tag)
        db.session.commit()

        result = tag.to_dict()
        assert result[TAG_NAME] == "Photography"
        assert result[TAG_ID] == tag.id


class TestTagRepr:
    """Test Tag.__repr__() method."""

    def test_repr_returns_correct_format(self, app_ctx, sample_tag):
        """Test __repr__ returns expected string format."""
        repr_str = repr(sample_tag)
        assert repr_str == f"<Tag {sample_tag.name}>"
        assert "Tag" in repr_str
        assert sample_tag.name in repr_str

    def test_repr_with_different_name(self, app_ctx):
        """Test __repr__ with different tag name."""
        tag = Tag(name="Camera")
        db.session.add(tag)
        db.session.commit()

        repr_str = repr(tag)
        assert repr_str == "<Tag Camera>"