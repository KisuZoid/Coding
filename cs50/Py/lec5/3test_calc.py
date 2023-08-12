import pytest

from calc import square

def test_positive():
    assert square(2) == 4
    assert square(3) == 9

def test_negative():
    assert square(-2) == 4
    assert square(-3) == 9

def test_zero():
    assert square(0) == 0

def test_str():
    with pytest.raises(TypeError):
        square("cat")
#raises() func. is the part of pytest library. that allows me to express that i expect an exception to be raised. | TypeError is expection here.
