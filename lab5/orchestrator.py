import multiprocessing as mp
import hashlib
import sys
import rpyc
import socket

running_nodes = {}

HASH_SIZE = 160
FT_LENGTH = 20


def start_nodes(n: int):
    free_ports = []

    #finding free ports in the system
    for i in range(2**n):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('', 0))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            free_ports.append(sock.getsockname()[1])

    #maps chord id's to localhost ports
    ids_to_ports = {int(hashlib.sha1(str(port).encode()).hexdigest(), 16): port for port in free_ports}
    ring = list(ids_to_ports.items())
    ring.sort(key=lambda x: x[0])

    print(ring)

    initial_finger_tables = {}
    for node_id, node_addr in ring:
        f_table = []
    
        finger = (node_id + 1) % 2**HASH_SIZE
        current_index = ring.index(lambda x: x[0] == node_id)
        if current_index == len(ring)-1:
            successor = ring[0]
        else:
            successor = ring[current_index + 1]
        f_table.append()
        initial_finger_tables[node_addr] = f_table

    print(initial_finger_tables)
    
class ChordNodeService(rpyc.Service):
    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    class exposed_Node(object):
        def __init__(self, ):
            pass

def chord_node_main(sock):
    pass

if __name__ == "__main__":
    start_nodes(int(sys.argv[1]))
    #start RPC server