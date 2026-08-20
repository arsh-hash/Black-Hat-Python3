import os 
import socket


# host to listen on 
host = '192.168.56.1'

def main():
    #create raw socket , bin to public interface
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0)) 

    #include ip headers in capture  
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    
    # read one packet
    print(sniffer.recvfrom(65565))

    #if we are on windows ,turn off the promiscous mode 
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        
if __name__ == '__main__':
    main()  



