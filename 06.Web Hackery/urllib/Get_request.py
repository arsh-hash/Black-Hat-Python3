# Get request using the urllib for python 3 

import urllib.parse
import urllib.request

# url = "https://baybee.co.in/"
url = "http://boodely.com/"

with urllib.request.urlopen(url) as response: 
    content = response.read()

print(content)
