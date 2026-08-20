from cryptor import decrypt
import requests

# Paste your URL here with /raw/ added
url = 'https://pastebin.com/raw/xxxxxxx'
r = requests.get(url)
decrypted = decrypt(r.content)
print('[+] Decrypted:', decrypted.decode())

