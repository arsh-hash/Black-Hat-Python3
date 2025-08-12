# simple test client  
#  which send and recevie the data from server 

import socket

target_host ="127.0.0.1"
target_port =9998

client =socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client.connect((target_host,target_port))

client.send(b"hello server") 

response=client.recv(1024)
print(response)

                                                

import socket

ip ="127.0.0.1"
port =9998

#Creating the client 
client =socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#connect the client
client.connect((ip,port))

#sending some data
a= input("enter message for sever :")
message=client.sendall(a.encode())

#receving the data 
response =client.recv(1024)
print(f"message from server =>{response.decode()}")

client.close()










#                                 don't connect to local server its connects with google server 
# import socket 

# targat_host = "www.google.com"
# targat_port = 80           # port for http 

# # create the socket/client object 
# client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)   #(IPV4,TCP CLIENT)

# #connect the client 
# client.connect((targat_host,targat_port))

# #send the data 
# client.send(b"GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n")   # send func

# #receive the data 
# response =client.recv(4096)                                #recv func 

# print(response.decode())
# client.close()


# # import the lib 
# # describe the host and port can be url/ip  than port 
# # make the socket client 
# # connect the client 
# # send data 
# # receive the data 
# # close the client 
