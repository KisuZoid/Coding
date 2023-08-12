#this is the way to collect the all tests in different directory
#pytest allows me to run this here too, but to do so, we have to make a file.
# in command prompt inside test directory: __init__.py
#even __init__.py is empty it is visual indicator to the python that treat folder not as a module or file alone but as a package.

from hello import hello

def test_default():
    assert hello() == "hello, world"

def test_argument():
    assert hello("Kisu") == "hello, Kisu"