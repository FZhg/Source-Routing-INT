#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet, IPOption
from scapy.all import Ether, IP, UDP
from scapy.fields import *
from scapy.layers.inet import _IPOption_HDR



def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

class SwitchTrace(Packet):
    fields_desc = [ BitField("swid", 0, 13),
                    BitField("qdepth", 0,13),
                    BitField("qtime", 0, 32),
                    BitField("portid",0,6)]
    def extract_padding(self, p):
                return "", p

class IPOption_INT(IPOption):
    name = "INT"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="int_headers",
                                  adjust=lambda pkt,l:l*2+4),
                    ShortField("count", 0),
                    PacketListField("int_headers",
                                   [],
                                   SwitchTrace,
                                   count_from=lambda pkt:(pkt.count*1)) ]


class SourceRoute(Packet):
   fields_desc = [ BitField("last_header", 0, 1),
                   BitField("swid", 0, 7)]

bind_layers(Ether, SourceRoute, type=0x1111)
bind_layers(SourceRoute, SourceRoute, last_header=0)
bind_layers(SourceRoute, IP, last_header=1)


def main():

    if len(sys.argv)<3:
        print('pass 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()
    print("sending on interface %s to %s" % (iface, str(addr)))

    while True:
        print()
        s = str(input('Type space separated switch_ids nums '
                          '(example: "2 3 2 2 1") or "q" to quit: '))
        if s == "q":
            break
        print()

        i = 0
        pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff');
        for p in s.split(" "):
            try:
                pkt = pkt / SourceRoute(last_header=0, swid=int(p))
                i = i+1
            except ValueError:
                pass
        if pkt.haslayer(SourceRoute):
            pkt.getlayer(SourceRoute, i).last_header = 1

        pkt = pkt / IP(
        dst=addr, options = IPOption_INT(count=0,
            int_headers=[])) / UDP(dport=4321, sport=1234) /  sys.argv[2]
        pkt.show2()
        sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
