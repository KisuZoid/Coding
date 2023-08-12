#2
from calculator import square

#categorised test : gives extra freedom that if any one test will fail, code will keep running for others. 
def test_positive():
    assert square(2) == 4
    assert square(3) == 9

def test_negative():
    assert square(-2) == 4
    assert square(-3) == 9

def test_zero():
    assert square(0) == 0

#uncategorised test: if any one line will failed to execute, then code will stop there.
"""
def test_square():
    assert square(2) == 4
    assert square(3) == 9
    assert square(-2) == 4
    assert square(-3) == 9
    assert square(0) == 0
"""

#pytest : it gives us hint that what must be wrong.
#url: docs.pytest.org
#using pip: pip install pytest
