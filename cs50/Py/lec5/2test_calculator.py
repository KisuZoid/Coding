from calculator import square

def test_square():
    assert square(2) == 4
    assert square(3) == 9
    assert square(-2) == 4
    assert square(-3) == 9
    assert square(0) == 0

#pytest : it gives us hint that what must be wrong.
#url: docs.pytest.org
#using pip: pip install pytest
