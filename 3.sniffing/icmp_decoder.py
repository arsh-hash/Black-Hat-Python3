import os
import socket
import ipaddress
import struct
import sys


class IP:
    def __init__(self, raw_buffer):
        header = struct.unpack('!BBHHHBBH4s4s', raw_buffer[:20])
        self.ver = header[0] >> 4
        self.ihl = header[0] & 0xF
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

        self.protocol_map = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
        self.protocol_name = self.protocol_map.get(self.protocol, str(self.protocol))
        if self.protocol_name == str(self.protocol):
            print(f"No protocol mapping for {self.protocol}")


class ICMP:
    def __init__(self, buff):
        header = struct.unpack('!BBHHH', buff)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]


def sniff(host):
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            raw_buffer = sniffer.recvfrom(65535)[0]
            if len(raw_buffer) < 20:
                continue

            ip_header = IP(raw_buffer[:20])
            print(f"Protocol: {ip_header.protocol_name} | {ip_header.src_address} → {ip_header.dst_address}")

            # If it's ICMP, parse and display more info
            if ip_header.protocol_name == 'ICMP':
                offset = ip_header.ihl * 4

                if len(raw_buffer) < offset + 8:
                    continue

                icmp_buffer = raw_buffer[offset:offset + 8]
                icmp_header = ICMP(icmp_buffer)

                print(f"ICMP → Type: {icmp_header.type} | Code: {icmp_header.code}")
                print(f"Version: {ip_header.ver} | Header Length: {ip_header.ihl} | TTL: {ip_header.ttl}")
                print('-' * 60)

    except KeyboardInterrupt:
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = socket.gethostbyname(socket.gethostname())

    sniff(host)
