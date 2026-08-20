import requests

url ="http://boodely.com/"
response =requests.get(url)    # get request 

print(response)

data = {"user":"tim", "passwd" :"31337"} 
response =requests.post(url,data=data)  # post request

# print(response.text)
print(response.content)
