#9
#package is a third party library that allows us to use more functionality.
#url: pypi.org
#cowsay package -- url pypi.org/project/cowsay
# pip comes with python, python's own package manager. it allows to install packages on pc or cloud by just running a command.
# example : for install cowsay, type "pip install cowsay" in command line.

import cowsay
import sys

if len(sys.argv) == 2:
    cowsay.cow("hello, " + sys.argv[1]) #cowsay.cow program gives output said by cow ;)
    cowsay.trex("hello, " + sys.argv[1]) #cowsay.trex program gives output said by trex :)