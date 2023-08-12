from hello import hello

def test_argument(): #this is how to use list for many tests.
    for name in ["Hermione", "Harry", "Ron"]:
        assert hello(name) == f"hello, {name}"

def test_default():
    assert hello() == "hello, world"

#test using pytest is passes as return value of hello("Kisu") is equal to hello, Kisu coz it returns the same value as hello, Kisu . 