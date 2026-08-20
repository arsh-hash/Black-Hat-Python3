from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from io import BytesIO

import base64
import zlib


def generate():
    # Generate 2048-bit RSA keypair
    new_key = RSA.generate(2048)
    
    # Export private and public keys
    private_key = new_key.exportKey()
    public_key = new_key.publickey().exportKey()
    
    # Save to files
    with open('key.pri', 'wb') as f:
        f.write(private_key)
        
    with open('key.pub', 'wb') as f:
        f.write(public_key)
        
    print("[+] Keys generated successfully!")
    print("[+] key.pri = private key (keep this on YOUR machine)")
    print("[+] key.pub = public key  (this goes on VICTIM machine)")


def get_rsa_cipher(keytype):
    # Read key file based on type ('pub' or 'pri')
    with open(f'key.{keytype}') as f:
        key = f.read()
        
    rsakey = RSA.importKey(key)
    
    # Return cipher object + key size in bytes
    return PKCS1_OAEP.new(rsakey), rsakey.size_in_bytes()


def encrypt(plaintext):
    # Step 1: Compress the data first
    compressed_text = zlib.compress(plaintext)
    
    # Step 2: Generate random 16-byte AES session key
    session_key = get_random_bytes(16)
    
    # Step 3: Encrypt data using AES-EAX mode
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(compressed_text)
    
    # Step 4: Encrypt the AES session key using RSA public key
    cipher_rsa, _ = get_rsa_cipher('pub')
    encrypted_session_key = cipher_rsa.encrypt(session_key)
    
    # Step 5: Pack everything into single payload
    # Layout: [encrypted_session_key][nonce][tag][ciphertext]
    msg_payload = encrypted_session_key + cipher_aes.nonce + tag + ciphertext
    
    # Step 6: Base64 encode for safe transport
    # encrypted = base64.encodebytes(msg_payload)
    encrypted = base64.b64encode(msg_payload)
    return encrypted


def decrypt(encrypted):
    # Step 1: Base64 decode back to bytes
    # encrypted_bytes = BytesIO(base64.decodebytes(encrypted))
    encrypted_bytes = BytesIO(base64.b64decode(encrypted)) 
    
    # Step 2: Load RSA private key
    cipher_rsa, keysize_in_bytes = get_rsa_cipher('pri')
    
    # Step 3: Unpack in same order we packed
    encrypted_session_key = encrypted_bytes.read(keysize_in_bytes)
    nonce                  = encrypted_bytes.read(16)
    tag                    = encrypted_bytes.read(16)
    ciphertext             = encrypted_bytes.read()
    
    # Step 4: Decrypt AES session key using RSA private key
    session_key = cipher_rsa.decrypt(encrypted_session_key)
    
    # Step 5: Decrypt actual data using AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    decrypted = cipher_aes.decrypt_and_verify(ciphertext, tag)
    
    # Step 6: Decompress and return
    plaintext = zlib.decompress(decrypted)
    return plaintext


# ========== TESTING ==========
if __name__ == '__main__':
    
    # First run: generate keys
    generate()
    
    # Test message
    plaintext = b'Hello! This is a secret message for testing cryptor.py'
    print(f"\n[*] Original  : {plaintext}")
    
    # Encrypt it
    encrypted = encrypt(plaintext)
    print(f"\n[*] Encrypted : {encrypted[:50]}...")  # show first 50 chars
    
    # Decrypt it
    decrypted = decrypt(encrypted)
    print(f"\n[*] Decrypted : {decrypted}")
    
    # Verify
    if plaintext == decrypted:
        print("\n[+] SUCCESS - Encrypt/Decrypt working correctly!")
    else:
        print("\n[-] FAILED - Something went wrong!")