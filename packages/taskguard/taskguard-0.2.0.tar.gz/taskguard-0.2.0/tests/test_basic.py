"""Basic tests for the taskguard package."""

def test_import():
    """Test that the package can be imported."""
    import taskguard  # noqa: F401
    assert taskguard.__version__ is not None
