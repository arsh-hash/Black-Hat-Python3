import ipaddress
import os
import socket
import struct
import sys

class IP:
    def __init__(self, raw_buffer):
        header = struct.unpack('!BBHHHBBH4s4s', raw_buffer)
        self.ver = header[0] >> 4                                # shift the bits right to get version   >>4
        self.ihl = header[0] & 0xF                               # to extract the header length 
        self.tos = header[1]
        self.len = header[2]
        self.id = header[3]
        self.offset = header[4]
        self.ttl = header[5]
        self.protocol = header[6]
        self.sum = header[7]
        self.src = header[8]
        self.dst = header[9]

        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        self.protocol_map = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}                  # protocols are in number in header
        try:
            self.protocol_name = self.protocol_map[self.protocol]
        except KeyError:
            self.protocol_name = str(self.protocol)
            print(f"No Protocol mapping for {self.protocol}")

def sniff(host):                                                             # check the os is windows or linux 
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP                                    # for windows
    else: 
        socket_protocol = socket.IPPROTO_ICMP                                # linux
 
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)                       # for seeing the meta data 

    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)                               # on the Promiscuous Mode

    try:
        while True:
            raw_buffer = sniffer.recvfrom(65535)[0]                                         # listening on every port 
            if len(raw_buffer) < 20:
                continue
            ip_header = IP(raw_buffer[:20])
            print(f"Protocol: {ip_header.protocol_name} | {ip_header.src_address} → {ip_header.dst_address}")
    except KeyboardInterrupt:
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = socket.gethostbyname(socket.gethostname())  # auto-detect IP
    sniff(host)
