import multiprocessing as mp
import hashlib, sys, rpyc, socket, time, threading
from rpyc.utils.server import ThreadedServer
from typing import Tuple


running_nodes = {}

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

    # maps chord id's to localhost ports
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

    
    addr, finger_table = list(initial_finger_tables.items())[0]

    # bootstrap_addr = free_ports[0]

    for addr, finger_table in list(initial_finger_tables.items()):
        p = mp.Process(target=chord_node_main, args=(bootstrap_addr, free_ports[1]))
        p.start()
        running_nodes[bootstrap_addr] = p

    for addr in free_ports[1:]:
        p = mp.Process(target=chord_node_main, args=(addr, bootstrap_addr))
        p.start()
        running_nodes[addr] = p

def chord_node_main(port_no: int, bootstrap_port_no: int = None):
    server = ThreadedServer(ChordNodeService(port=port_no, bootstrap_node=bootstrap_port_no), port=port_no)
    server.start()
    
class ChordNodeService(rpyc.Service):

    FT_LENGTH = 20
    HASH_SIZE = 160

    def __init__(self, port, bootstrap_node):
        super().__init__()
        #array containing objects of the format (finger, (id_successor, port_successor))
        print(f"starting on port: {port}, bootstrap: {bootstrap_node}")
        self.exposed_id = hash(port)
        self.exposed_port = port
        self.next_finger = 0
        
        #creating chord ring from scratch
        if bootstrap_node is None:
            self.exposed_successor = (self.exposed_id, self.exposed_port) #NÃO FAZ SENTIDO!!!
        
        #joining chord ring from a known bootstrap node
        else:    
            entry_node = rpyc.connect("localhost", bootstrap_node)
            self.exposed_successor = entry_node.root.find_successor(self.exposed_id)

        self.exposed_predecessor = None
        self.finger_table = [None]*self.FT_LENGTH
        self.finger_table[0] = {"finger": (self.exposed_id+1) % 2**self.HASH_SIZE, "successor": self.exposed_successor}

        # threading.Thread(target=self.housekeeping).start()

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def housekeeping(self):
        while True:
            time.sleep(0.25)
            # with self.lock:
            self.fix_fingers()
            self.stabilize()

    def stabilize(self):
        conn = rpyc.connect("localhost", self.exposed_successor[1])
        x: Tuple[int, int] = conn.root.predecessor
        if x is not None and (x[0] > self.exposed_id and x[0] < self.exposed_successor[0]):
            self.exposed_successor = x

        #repetition is necessary, as the previous step could have changed the successor, invalidating the connection
        conn = rpyc.connect("localhost", self.exposed_successor[1])
        conn.root.notify((self.exposed_id, self.exposed_port))

    def fix_fingers(self):
        self.next_finger += 1
        if self.next_finger >= self.FT_LENGTH:
            self.next_finger = 0
        finger = (self.exposed_id + 2**self.next_finger) % 2**self.HASH_SIZE
        print(f"next finger: {self.next_finger}")
        successor = self.exposed_find_successor(finger)
        # with self.lock:
        self.finger_table[self.next_finger] = {
            "finger": finger, 
            "successor": successor
        }
    
    def exposed_notify(self, node: Tuple[int, int]):
        if self.exposed_predecessor is None or (node[0] > self.exposed_predecessor[0] and node[0] < self.exposed_id):
            self.exposed_predecessor = node

    # def expand_finger_table(self):
    #     peer = rpyc.connect("localhost", self.exposed_successor[1])
    #     for i in range(1, self.FT_LENGTH):
    #         finger = (self.exposed_id + 2**i) % 2**HASH_SIZE
    #         ith_finger_successor = peer.root.find_successor(finger)
    #         self.finger_table.append((finger, ith_finger_successor))
    #     self.stable = True

    def closest_preceding_node(self, id: int) -> Tuple[int, int]:
        for i in range(self.FT_LENGTH - 1, -1, -1):
            if self.finger_table[i] is None: continue
            if self.finger_table[i]["finger"] > self.exposed_id and self.finger_table[i]["finger"] < id:
                return self.finger_table[i]["successor"]
        
        return (self.exposed_id, self.exposed_port)

    def exposed_find_successor(self, id: int) -> Tuple[int, int]:
        # with self.lock:
        print(f"id: {id}, n: {self.exposed_id}, succ: {self.exposed_successor}")
    
        if id > self.exposed_id and id <= self.exposed_successor[0]:
            return self.exposed_successor
        else:
            pred = self.closest_preceding_node(id)
            peer = rpyc.connect("localhost", pred[1])
            return peer.root.find_successor(id)
            

    def exposed_test(self):
        return "hey"
        

class OrchestratorService(rpyc.Service):
    pass


if __name__ == "__main__":
    start_nodes(int(sys.argv[1]))
    print("Running Chord nodes:")
    [print(f"localhost:{port}") for port in running_nodes.keys()]
    # server = ThreadedServer(OrchestratorService, port=9000)
    # server.start()