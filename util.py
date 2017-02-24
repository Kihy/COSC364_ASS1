def check_id(router_id):
    if router_id > 64000 or router_id<1:
        return False

def check_port(port_num):
    if port_num <1024 or port_num>64000:
        return False

def read_config(filename):
    router_id=None
    input_ports=[]
    output_ports=[]
    conf=open(filename)
    for line in conf.readlines():
        line=line.rstrip()
        if line.startswith("//") or line=="":
            continue

        if line.startswith("router-id"):
            router_id=int(line.split()[1])

        if line.startswith("input-ports"):
            input_ports=list(map(int,line.split()[1].split(",")))

        if line.startswith("outputs"):
            output_port=line.split()[1].split(",")
            for port in output_port:
                output_ports.append(list(map(int,port.split("-"))))

    print(router_id)
    print(input_ports)
    print(output_ports)

read_config("conf1.txt")
