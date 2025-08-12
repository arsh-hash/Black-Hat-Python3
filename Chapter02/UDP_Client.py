# simple code 
import socket

client_socket =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

client_socket.sendto(b"hello from the client" ,('127.0.0.1',12345))

message,server =client_socket.recvfrom(1024)

print(f"Message form server {message.decode()}")

client_socket.close()







##                                 code by book 
# import socket

# target_host ="127.0.0.1"
# target_port =9997

# #create a socket /client object 
# client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)    # (IPV4 , UDP)

# # send some data 
# client.sendto(b"AABBBCCC",(target_host,target_port))    # sendto func

# #recevie some data 
# data,addr =client.recvfrom(4096)                   #recvfrom func

# print(data.decode)
# client.close()



