from io import BytesIO
from lxml import etree

import requests

url = "http://nostarch.com/"

r =requests.get(url)  # get 
content =r.content   # content is a type of "bytes"


parser =etree.HTMLParser()
content=etree.parse(BytesIO(content),parser=parser) # parse into tree
for link in content.findall("//a"): 
    print(f"{link.get("href")} ==> {link.text}")