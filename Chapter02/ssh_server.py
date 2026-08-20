import os 
import paramiko
import socket
import sys
import threading

CWD= os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD,'test_rsa.key'))

class Server (paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
           return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if username == "admin" and password == "secret":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED



if __name__ == "__main__":
    server ='192.168.56.100'
    ssh_port =22
    try:
        sock =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.bind((server,ssh_port))
        sock.listen(100)
        print('[+] Listening for Connection ... ')
        client,addr = sock.accept()
    except Exception as e:
        print('[-] Listen Failed: '+ str(e))
        sys.exit(1)
    else:
        print('[+] Got a Connection !',client,addr)


bhsession = paramiko.Transport(client)
bhsession.add_server_key(HOSTKEY)
server =Server()
bhsession.start_server(server=server)

chan =bhsession.accept(20)
if chan is None:
    print('*** No channel')
    sys.exit(1)

print('[+] Authenticated !')
print(chan.recv(1024))
chan.send('welcome to bh_shh')
try:
    while True:
        command =input('enter command')
        if command != 'exit':
            chan.send(command)
            r =chan.recv(8192)
            print(r.decode())
        else:
            chan.send('exit')
            print('exiting')
            bhsession.close()
            break
except KeyboardInterrupt:
    bhsession.close()