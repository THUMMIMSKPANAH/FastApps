import pytest
from fastapps.core.widget import Widget


@pytest.fixture
def sample_widget():
    """Create a sample widget for testing."""
    class TestWidget(Widget):
        def render(self):
            return {"message": "Hello, World!"}

    return TestWidget()


@pytest.fixture
def mock_server():
    """Mock server configuration for testing."""
    return {
        "host": "localhost",
        "port": 8000,
        "reload": False
    }
