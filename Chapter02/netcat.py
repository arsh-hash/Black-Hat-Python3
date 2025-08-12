import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


class NetCat:
    def __init__(self,args,buffer=None):
        self.args =args
        self.buffer =buffer
        self.socket =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        print("[DEBUG] NetCat initialized.") 

    def run(self):
        if self.args.listen:
            print("[DEBUG] Running as listener.") 
            self.listen()
        else:
            print("[DEBUG] Running as sender (client).") 
            self.send()

    def send(self):
        try:
            print(f"[DEBUG] Attempting to connect to {self.args.target}:{self.args.port}") 
            self.socket.connect((self.args.target,self.args.port))
            print("[DEBUG] Connected successfully.") 

            if self.buffer:
                print(f"[DEBUG] Sending initial buffer: {len(self.buffer)} bytes") 
                self.socket.send(self.buffer)
                print("[DEBUG] Initial buffer sent.") 


            while True:
                recv_len=1
                response =''
                print("[DEBUG] Waiting for server response...") 
                while recv_len:
                    data =self.socket.recv(4096)
                    recv_len =len(data)
                    print(f"[DEBUG] Received {recv_len} bytes.") 
                    if not data:
                        print("[DEBUG] Server closed connection. Exiting.")
                        break 
                    try:
                        response += data.decode('utf-8', errors='replace') # Added error handling
                    except UnicodeDecodeError:
                        print(f"[ERROR] UnicodeDecodeError while decoding: {data}")
                        response += data.hex() # Show raw bytes if decode fails
                    
                    if recv_len  < 4096:
                        print("[DEBUG] Received less than 4096 bytes, assuming end of message.") 
                        break
                
                if not response and not recv_len: 
                    print("[DEBUG] No response and connection closed. Exiting loop.")
                    break

                if response:
                    print(f"[DEBUG] Full response received:\n{response}") 
                    print(response, end='') 
                    try:
                        buffer = input('> ')
                        buffer += '\n'
                        self.socket.send(buffer.encode())
                    except EOFError: # Handles Ctrl+D
                        print("[DEBUG] EOFError, usually Ctrl+D. Exiting.")
                        break # Exit loop if input stream ends
                else: 
                    print("[DEBUG] Empty response from server, but still connected. Waiting for more data...")


        except KeyboardInterrupt:
            print('user terminated')
        except ConnectionRefusedError: 
            print(f"[ERROR] Connection refused. Is the listener running on {self.args.target}:{self.args.port}?")
        except Exception as e: 
            print(f"[ERROR] Client error: {e}")
        finally:
            print("[DEBUG] Closing client socket.") 
            self.socket.close()
            sys.exit()

    
    def listen(self):
        print(f"[DEBUG] Binding to {self.args.target}:{self.args.port}") 
        self.socket.bind((self.args.target,self.args.port))
        self.socket.listen(5)
        print("[DEBUG] Listening for connections...") 

        while True:
            client_socket, addr =self.socket.accept()
            print(f"[DEBUG] Accepted connection from {addr[0]}:{addr[1]}") 
            client_thread = threading.Thread(
                target=self.handle,
                args=(client_socket,)
            )
            client_thread.start()
    

    def handle(self,client_socket):
        print("[DEBUG] Handling client connection.") 
        if self.args.execute:
            print(f"[DEBUG] Executing command: {self.args.execute}") 
            output =execute(self.args.execute)
            client_socket.send(output.encode())
            print("[DEBUG] Executed command output sent.") 

        elif self.args.upload:
            print(f"[DEBUG] Ready to receive file: {self.args.upload}") 
            file_buffer = b''
            while True:
                data =client_socket.recv(4096)
                if data:
                    file_buffer+=data
                else:
                    break
            with open(self.args.upload,'wb') as f:
                f.write(file_buffer)
            message = f'saved file {self.args.upload}'
            client_socket.send(message.encode())
            print(f"[DEBUG] File '{self.args.upload}' saved and confirmation sent.") 
        

        elif self.args.command:
            print("[DEBUG] Command shell requested.") 
            cmd_buffer =b''
            while True:
                try:
                    client_socket.send(b'BHP: #>')
                    print("[DEBUG] Sent shell prompt to client.") 
                    #while '\n'  not in cmd_buffer.decode('utf-8', errors='replace'): 
                    while '\n' not in cmd_buffer.decode('utf-8', errors='replace'):
                        data_recv = client_socket.recv(64)
                        if not data_recv: 
                            print("[DEBUG] Client disconnected while waiting for command input.")
                            raise ConnectionAbortedError("Client disconnected") 
                        cmd_buffer += data_recv
                    
                    cmd_to_execute = cmd_buffer.decode('utf-8', errors='replace').strip()
                    print(f"[DEBUG] Received command: '{cmd_to_execute}'") 
                    response = execute(cmd_to_execute)
                    if response:
                        client_socket.send(response.encode())
                        print("[DEBUG] Command output sent to client.") 
                    cmd_buffer = b""
                except ConnectionAbortedError: 
                    print("[DEBUG] Client connection aborted (possibly disconnected).")
                    break 
                except Exception as e:
                    print(f'[ERROR] Server handle failed: {e}')
                    break 
            client_socket.close() 
            print("[DEBUG] Client handler finished.")


def execute(cmd):
    cmd =cmd.strip()
    if not cmd:
        return
    print(f"[DEBUG] Executing system command: '{cmd}'") 
    try:
        output =subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT, text=True, encoding='utf-8') # text=True for string output
        print("[DEBUG] Command executed successfully.") 
        return output
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command execution failed: {e}") 
        return f"Error executing command: {e.output}"
    except FileNotFoundError:
        return f"Error: Command '{shlex.split(cmd)[0]}' not found."
    except Exception as e:
        return f"Unexpected error during command execution: {e}"


if __name__ == "__main__":
    parsar = argparse.ArgumentParser(description='BHP Net Tool',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       epilog=textwrap.dedent(""" Example:
                                                                netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
                                                                netcat.py -t 192.168.1.108 -p 5555 -l  -u=mytest.txt # upload to test
                                                                netcat.py -t 192.168.1.108 -p 5555 -l  -e=" cat /etc/passwd" # execute command
                                                                echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135  #echo text to server port 135
                                                                netcat.py -t 192.168.1.108 -p 5555 # connect to server
                                                                """))

parsar.add_argument('-c','--command' ,action="store_true" ,help='command shell')
parsar.add_argument('-e','--execute', help="execute specific command")
parsar.add_argument('-l','--listen',action='store_true', help="listen")
parsar.add_argument('-p','--port',type=int,default=5555,help='specified port')
parsar.add_argument('-t','--target',default='0.0.0.0',help='specified the ip')
parsar.add_argument('-u','--upload',help='upload files')

args=parsar.parse_args()


buffer = b'' # Initialize buffer as empty bytes

if not args.listen and not sys.stdin.isatty(): 
    buffer = sys.stdin.read().encode()

nc =NetCat(args,buffer) # Pass the (potentially empty) buffer
nc.run()