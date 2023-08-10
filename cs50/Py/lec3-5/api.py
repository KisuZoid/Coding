#10
#here api refers third party services that we can write code that talk to.
#python has popular package called "requests" that allows to web request/internet request using python code like you are the browser it self.
# url: pypi.org/project/requests
# using pip : "pip install requests" run this on your command code.

import requests
import sys

if len(sys.argv) != 2:
    sys.exit() #means length of sys.argv is not 2 then exit the program.

response = requests.get("https://itunes.apple.com/search?entity=song&limit=1&term=" + sys.argv[1]) #here term=sys.argv[1]
print(response.json()) #means it ensure that the data i am getting back is json() format.