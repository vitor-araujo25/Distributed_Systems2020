import multiprocessing as mp
import hashlib
import sys
import rpyc
import socket
from rpyc.utils.server import ThreadedServer
from rpyc.utils.helpers import classpartial
import time

running_nodes = {}

HASH_SIZE = 160
FT_LENGTH = 20

def hash(key: str):
    return int(hashlib.sha1(str(key).encode()).hexdigest(), 16)

def start_nodes(n: int):
    free_ports = []

    #finding free ports in the system
    for i in range(2**n):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('', 0))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            free_ports.append(sock.getsockname()[1])

    #maps chord id's to localhost ports
    ids_to_ports = {hash(port): port for port in free_ports}
    ring = list(ids_to_ports.items())
    ring.sort(key=lambda x: x[0])

    initial_finger_tables = {}
    for idx, elem in enumerate(ring):
        node_id, node_addr = elem
   
        finger = (node_id + 1) % 2**HASH_SIZE
        if idx == len(ring)-1:
            successor = ring[0]
        else:
            successor = ring[idx + 1]

        initial_finger_tables[node_addr] = [(finger, successor)]

    #TODO: start a node process for each port in initial_finger_tables.keys()

    print(initial_finger_tables.keys())


    for addr, finger_table in initial_finger_tables.items():
        p = mp.Process(target=chord_node_main, args=(addr, finger_table))
        p.start()
        running_nodes[addr] = p
    
    [print(f"localhost:{port}") for port in running_nodes.keys()]

    for addr, process in running_nodes.items():
        print("attempting join")
        process.join()

def chord_node_main(port_no: int, f_table):
    service = classpartial(ChordNodeService, port=port_no, f_table=f_table)
    server = ThreadedServer(service, port=port_no)
    server.start()
    
class ChordNodeService(rpyc.Service):

    def __init__(self, port, f_table):
        super().__init__()
        self.finger_table = f_table
        self.successor = self.finger_table[0]
        self.id = hash(port)

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass
    
    def exposed_test(self):
        return "hey"

    def exposed_get_sucessor(self):
        return self.successor



if __name__ == "__main__":
    start_nodes(int(sys.argv[1]))
    #start RPC server