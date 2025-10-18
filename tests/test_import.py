"""Test basic package imports."""


def test_import_fastapps():
    """Test that fastapps package can be imported."""
    import fastapps

    assert fastapps is not None


def test_import_widget():
    """Test that Widget class can be imported."""
    from fastapps.core.widget import Widget

    assert Widget is not None


def test_import_cli():
    """Test that CLI module can be imported."""
    from fastapps.cli.main import cli

    assert cli is not None
