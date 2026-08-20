from bs4 import BeautifulSoup as bs
import requests

url ="http://nostarch.com/"

r =requests.get(url)
tree=bs(r.text,"html.parser")   # parse into tree
for link in tree.find_all("a"):  # find all "a"  anchor elements
    print(f"{link.get("href")} ==> {link.text}")