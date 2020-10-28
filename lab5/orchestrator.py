import multiprocessing as mp
import sys, rpyc, socket, time, threading
from typing import Tuple
from chord_node import ChordNodeService
from utils import sha, NodeID

running_nodes = {}
PORT = 10000

def start_nodes(n: int):
 
    ports = {i: PORT + i + 1 for i in range(2**n)}
    
    for i in range(2**n):
    
        finger_table = []

        for j in range(n):
            finger = (i + 2**j) % 2**n
            entry = {
                "finger": finger, 
                #since we are sure to have a running node for each 0 <= id < 2^n
                #the closest preceding node to any id is id-1, making any id's successor
                #equal to the id itself
                "successor": NodeID(node_id=finger, port=ports[finger])
            }
            finger_table.append(entry)

        node = ChordNodeService(node_id=i, port=ports[i], finger_table=finger_table)
        p = mp.Process(target=node.start)
        p.start()
        running_nodes[(i, ports[i])] = p

class OrchestratorService(rpyc.Service):
    pass


if __name__ == "__main__":
    start_nodes(int(sys.argv[1]))
    print("Running Chord nodes:")
    [print(f"localhost:{port}") for node_id, port in running_nodes.keys()]
    # server = ThreadedServer(OrchestratorService, port=9000)
    # server.start()
