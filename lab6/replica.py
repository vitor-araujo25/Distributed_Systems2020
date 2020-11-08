import rpyc, sys
from rpyc.utils.server import ThreadedServer
from typing import List, Tuple
import multiprocessing as mp
import time
from utils import *

#defined by project specification
N = 4

class ReplicaNode(rpyc.Service):
    def __init__(self, my_id):
        self.id = my_id
        self.X = 0
        self.can_write = True if self.id == 1 else False
        self.peer_ports = [5000+i for i in range(1,N+1) if i != self.id]
        self.update_history: List[Tuple[int, int]] = []

def node_start(node_instance):
    #TODO: define signal handler that calls node_instance.stop()
    node_instance.start()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong parameter count.")
        usage()
        sys.exit(1)
    try:
        replica_id = int(sys.argv[1])
        if replica_id > N or replica_id < 1:
            raise ValueError
    except ValueError:
        print(f"ID parameter must be an integer in the range [1,{N}]!")
        usage()
        sys.exit(1)
    
    #start replica node
    local_replica_port = 5000 + replica_id
    replica_node = ThreadedServer(ReplicaNode(replica_id), port=local_replica_port)
    replica_process = mp.Process(target=node_start, args=(replica_node,))
    replica_process.start()

    #start user interaction loop
    time.sleep(0.25)
    replica = rpyc.connect("localhost", port=local_replica_port)

    print(f"Replica {replica_id} started. Interact with it via the prompt below.")
    print(f"To list the possible commands, type \"help\" or \"?\".")
    while True:
        print("> ", end="")
        user_input = input()
        user_input = user_input.lower().split(' ')
        command = user_input[0]
        params = user_input[1:]
        param_count = len(params)

        try:
            if command == "read":
                assert param_count == 0
                #read X from replica
            
            elif command == "history":
                assert param_count == 0
                #read history from replica
            
            elif command == "set":
                assert param_count == 1
                assert is_int_coercible(params[0])
                value = int(params[0])
                #write value to X in current replica

            elif command == "quit":
                assert param_count == 0
                print("Quitting...")
                sys.exit(0)

            elif command in ("help", "?"):
                assert param_count == 0
                print_help()

            else:
                raise InvalidCommandException

        except AssertionError:
            print(f"Wrong parameters for command '{command}'. Please check instructions by running 'help'.")
        except InvalidCommandException:
            print(f"Command '{command}' is unknown.")
