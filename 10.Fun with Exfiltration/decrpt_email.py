# Quick decrypt test — run this separately
from cryptor import decrypt

# Paste the encrypted content here
received = b''
decrypted = decrypt(received)
print(decrypted)