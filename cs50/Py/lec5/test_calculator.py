#1
from calculator import square

def main():
    test_square()

def test_square():
    assert square(2) == 4
    assert square(3) == 9
    #or
    '''
    if square(2) != 4:
        print("2 squared was not 4")
    if square(3) != 9:
        print("3 squared was not 9")
    '''

if __name__ == "__main__":
    main()

# assert keyword is allows to assert something is true. and if it is originally true nothing is going to happen but is originally false then seeing some kind of error generally AssertionError. 