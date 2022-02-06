# -*- encoding: cp949 -*-
import socket
import random
import struct



def error_checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        w = msg[i] + (msg[i + 1] << 8)
        s = s + w
    s = (s >> 16) + (s & 0xffff)
    s = s + (s >> 6)
    s = ~s & 0xfff
    return s

def icmp():
    type = 8
    code = 0
    chksum = 0
    id = random.randint(0, 0xFFFF)
    seq = 1
    real_chksum = error_checksum(struct.pack('!BBHHH', type, code, chksum, id, seq))
    icmp_pkt = struct.pack('!BBHHH', type, code, socket.htons(real_chksum), id, seq)
    return icmp_pkt


s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
import time
while True:
    s.sendto(icmp(), ('192.168.0.1', 0))
    time.sleep(1)

