import pytest
from fastapps.core.widget import Widget


class SampleWidget(Widget):
    """Sample widget for testing."""

    def render(self):
        return {"status": "ok", "data": "test"}


def test_widget_creation():
    """Test widget can be instantiated."""
    widget = SampleWidget()
    assert widget is not None


def test_widget_render(sample_widget):
    """Test widget render method."""
    result = sample_widget.render()
    assert isinstance(result, dict)
    assert "message" in result
    assert result["message"] == "Hello, World!"


def test_widget_inheritance():
    """Test widget inherits from Widget base class."""
    widget = SampleWidget()
    assert isinstance(widget, Widget)
