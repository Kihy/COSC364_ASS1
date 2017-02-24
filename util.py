import sys

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
