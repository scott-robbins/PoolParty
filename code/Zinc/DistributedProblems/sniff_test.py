import numpy as np
import utils
import time
import sys
import os
tic = time.time()


def load_log(file_name):
    traffic = {'IP': [], 'ARP': [], 'DNS': []}
    for line in utils.swap(file_name, False):
        try:
            traffic['IP'].append(line.split(' IP ')[1].split(', length')[0])
        except IndexError:
            pass
        try:
            traffic['ARP'].append(line.split('ARP')[1].split(', length')[0])
        except IndexError:
            pass
    ip_packets = []
    udp = 0
    # Label Known Packet Types
    for ip_pkt in traffic['IP']:
        try:
            sender = ip_pkt.split(' > ')[0]
        except:
            pass
        try:
            receiver = ip_pkt.split(' >')[1].split(': ')[0]
        except IndexError:
            pass
        try:
            head = ip_pkt.split(':')[1]
        except IndexError:
            pass
        packet = [sender, receiver, head]
        ip_packets.append(packet)
        if 'UDP' in head.split(' '):
            udp += 1
    arps = []
    for arp in traffic['ARP']:
        try:
            request = arp.split('Request ')[1].split(' tell ')[0]
        except IndexError:
            pass
        try:
            sender = arp.split(' tell ')[1]
        except IndexError:
            pass
        arps.append([request, sender])
    # Display Distribution of Results
    for bin in traffic.keys():
        print '%d %s Packets Logged' % (len(traffic[bin]), bin)
    print '%d UDP Packets Logged' % udp
    ex = np.random.random_integers(-1,100,1)[0]
    print traffic['ARP'].pop(ex)
    print arps.pop(ex)


def search_logs(target):
    connections = []



file_in = 'example_traffic.sniff'
if '-i' in sys.argv and len(sys.argv) >= 3:
    file_in = sys.argv[2]

nx_traffic = load_log(file_in)


print 'FINISHED [%ss Elapsed]' % str(time.time()-tic)
