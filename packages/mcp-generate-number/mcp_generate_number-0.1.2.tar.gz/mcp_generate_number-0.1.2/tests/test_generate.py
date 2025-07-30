from server import generate_number

def test_range():
    assert 0 <= generate_number() <= 100 