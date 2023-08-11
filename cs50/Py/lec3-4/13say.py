#13 importing own library no 12(saying.py) in python 
import sys

from saying import hello

if len(sys.argv) == 2:
    hello(sys.argv[1])