import socket
import select
import time
import random
from util import *

LOCALHOST="127.0.0.1"
PERIODIC_TIMER=25



class Router(object):
    """docstring for Router."""
    def __init__(self, router_id):
        self.timer=time.time()
        self.router_id=router_id
        self.routing_table=[]
        self.input_sockets=[]

    def add_input_socket(self, port_num):
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.bind((LOCALHOST,port_num))
        self.input_sockets.append(sock)

    def add_routing_table(self, port,metric,router_id):
        self.routing_table.append([port,metric,router_id])



    def start(self):
        t = time.time()
        print(t)
        t2=PERIODIC_TIMER
        while True:
            if (time.time() - t) >= t2:
                print(time.time()-t)
                t2=PERIODIC_TIMER + random.uniform(0, 10)
                print("13  "+str(t2))
                t += t2
                self.send(12)
                #self.print_table()
            inputready, outputready,exceptrdy = select.select(self.input_sockets, [],[],0.5)
            for s in inputready:
                data,addr=s.recvfrom(1024)
                print(data)

    def send(self, port_num):
        self.input_sockets[0].sendto(b"hello",(LOCALHOST,self.routing_table[0][0]))
        print("send")
