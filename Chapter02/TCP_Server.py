# server which sends the data as well receive the data from client 
import socket 

ip = "0.0.0.0"
port= 9998

client =socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client.bind((ip,port))
print("server is binded")

client.listen(5)
print("client is listening ")

while  True: 
    client_socket,address =client.accept()
    print(f"connection form {address}")

    client_socket.send(b"hello from server")
    print("data sended")

    message =client_socket.recv(1024).decode()
    print(message)

    client_socket.close()



#                                       using the threading and auto closing the cleints 
import socket 
import threading

ip ="0.0.0.0"          # use 0.0.0.0 for receving request from any ips local and internet 
port = 9998            # use 127.0.0.1 for local host only 

def main():
    server =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((ip,port))
    server.listen(5)                #limit how much ips our server will listen too
    print(f"[*] Listening on {ip}:{port}")

    while True:
        client,address =server.accept()
        print(f"[*] Accepted connection from {address[0]}:{address[1]}")
        client_handler =threading.Thread(target=handler_client,args=(client,))
        client_handler.start()

def handler_client(cleint_socket):
    with cleint_socket as sock:
        request = sock.recv(1024)
        print(f"[*] Recevied: {request.decode("utf-8")}")
        sock.send(b"message recevied ")

if __name__ == "__main__":
    main()
