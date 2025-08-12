# creating the server 

import socket


server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 

#socket.AF_INET => socket using the ip4 
#socket.sock_DRAM => socket using the UDP Protocol 

server_socket.bind(('127.0.0.1',12345))   #bind the socket => join ip and port
print("Binding is Done")

print("UDP server is listening ")

while True:
    message,address =server_socket.recvfrom(1024)
    print(f"Recevied message from {address}:{message.decode()}")
    server_socket.sendto(b"hello from UDP Server",address)


