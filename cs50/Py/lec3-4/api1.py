#11
#python also comes with special library called json that allows to manipulate json  data. 
#url: docs.python.org/3/library/json.html
import json
import requests
import sys

if len(sys.argv) != 2:
    sys.exit()

response = requests.get("https://itunes.apple.com/search?entity=song&limit=50&term=" + sys.argv[1])
print(json.dumps(response.json(), indent=2)) #json.dumps here s in dump stands for string. i.e. dump string.
#indent=2 indent gonna indent everthing atleast 2 spaces.
#using variable response, we are making http request using python to the server just like we type url into a browser.


#now we are grabing the json object from that server response(which is in json() formate).
#json object are written in curly bracket. and that object has the key "results" key it is also a list and "trackName"
o = response.json()
for result in o["results"]:
    print(result["trackName"])
