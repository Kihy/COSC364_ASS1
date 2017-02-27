import sys
import struct

class Rip_packet:
    """a rip v2 packet"""
    def __init__(self, router_id):
        self.command=2
        self.version=2
        self.router_id=router_id
        self.entry_table=[]

    def add_entry(self,address_family,route_tag,router_id,subnet_mask,next_hop,metric):
        self.entry_table.append((address_family,route_tag,router_id,subnet_mask,next_hop,metric))

    def dump(self):
        #header
        packet=struct.pack('BBH',self.command,self.version,self.router_id)
        #add entry_table
        for row in self.entry_table:
            packet.append(struct.pack('HHIIII',row[0],row[1],row[2],row[3],row[4],row[5]))
        return packet

def load(self,packet):
    num_entry=(len(packet)-4)/20
    command,version,router_id=struct.unpack('BBH',packet[0:4])
    rip=Rip_packet(router_id)
    for i in range(num_entry):
        address_family,route_tag,router_id,subnet_mask,next_hop,metric=struct.unpacket("HHIIII",packet[4+i*20:4+(i+1)*20])
        rip.add_entry(address_family,route_tag,router_id,subnet_mask,next_hop,metric)
    return rip


def check_id(router_id):
    if router_id > 64000 or router_id<1:
        raise ValueError("Router ID out of bounds.")

def check_port(port_num):
    if port_num <1024 or port_num>64000:
        raise ValueError("port number out of bounds.")

def read_config(filename):
    router_id=None
    input_ports=[]
    output_ports=[]
    conf=open(filename)
    for line in conf.readlines():
        line=line.rstrip()
        if line.startswith("//") or line=="":
            continue
        try:
            if line.startswith("router-id"):
                router_id=int(line.split()[1])

            if line.startswith("input-ports"):
                input_ports=list(map(int,line.split()[1].split(",")))

            if line.startswith("outputs"):
                output_port=line.split()[1].split(",")
                for port in output_port:
                    output_ports.append(list(map(int,port.split("-"))))
        except ValueError as e:
            print(e.args[0])
            sys.exit()
        except IndexError as e:
            print("missing inputs")
            sys.exit()
    try:
        if router_id==None:
            raise ValueError("Router ID not set")
    except ValueError as e:
        print(e.args[0])
        sys.exit()
    return router_id, input_ports, output_ports
print(read_config("conf1.txt"))
