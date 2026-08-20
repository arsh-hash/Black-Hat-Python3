import ipaddress
import os 
import sys
import socket
import struct
import threading
import time 

# subnet to target 
subnet = '192.168.56.0/24'
# magic string we'll check ICMP responses for 
message = 'PYTHONRULES!'

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

# this sprays for out UDP datagrams with our magic message 
def udp_sender():
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(subnet).hosts():
            # sender.sendto(bytes(message,'utf8')(str(ip),65212))
            sender.sendto(bytes(message, 'utf8'), (str(ip), 65212))



class Scanner:
    def __init__(self,host):
        self.host= host 
        if os.name == 'nt':
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol =socket.IPPROTO_ICMP

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        self.socket.bind((host,0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if os.name =='nt':
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        
    def sniff(self):
        hosts_up = set([f'{str(self.host)} *'])
        try:
            while True:
                #read the packet 
                raw_buffer = self.socket.recvfrom(65535)[0]
                #create an ip header form the first 20 bytes
                ip_header = IP(raw_buffer[0:20])
                #if its icmp , we want it 
                if ip_header.protocol_name == 'ICMP':
                    offset = ip_header.ihl * 4
                    icmp_buffer = raw_buffer[offset:offset + 8]
                    icmp_header = ICMP(icmp_buffer)
                    # to check for type 3 and code 
                    # if icmp_header.code == 3 and icmp_header.type == 3:
                    if icmp_header.type == 3 and icmp_header.code == 3:
                         if ipaddress.ip_address(ip_header.src_address) in ipaddress.IPv4Network(subnet):
                          # make sure it has our magic message 
                            if raw_buffer[len(raw_buffer) - len(message):] == bytes(message,'utf8'):
                                tgt = str(ip_header.src_address)
                                if tgt !=self.host and tgt not in hosts_up:
                                   hosts_up.add(str(ip_header.src_address))
                                print(f"host up : {tgt}")
        except KeyboardInterrupt:
            if os.name =='nt':
                self.socket.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)
            print('\nUser interrupted')
            if hosts_up:
                print(f'\n\nSummary: hosts up on {subnet}')
 
            for host in sorted(hosts_up):
                # print(f'{host}')
                print(f"[+] Host up: {tgt}")

            print('')
            sys.exit()


if __name__ =="__main__":
    if len(sys.argv)==2:
        host =sys.argv[1]
    else:
        # host = socket.gethostbyname(socket.gethostname())
        host ='192.168.56.1'
s =Scanner(host)
time.sleep(5)
t =threading.Thread(target=udp_sender)
t.start()
s.sniff()