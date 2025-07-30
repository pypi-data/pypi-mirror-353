from mcp_generate_number.server import _generate_number, _generate_string
import re

def test_generate_number_range():
    """Tests that generate_number returns a number within the expected range."""
    for _ in range(100):
        num = _generate_number()
        assert isinstance(num, int)
        assert 0 <= num <= 100

def test_generate_string():
    """Tests that generate_string returns a string of the correct length and content."""
    # Test with default length
    s = _generate_string()
    assert isinstance(s, str)
    assert len(s) == 10
    assert re.match("^[a-z]+$", s)

    # Test with a custom length
    s = _generate_string(length=5)
    assert isinstance(s, str)
    assert len(s) == 5
    assert re.match("^[a-z]+$", s) 