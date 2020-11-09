import rpyc, sys, logging, time, signal
from rpyc.utils.server import ThreadedServer
from typing import List, Tuple
import multiprocessing as mp
from threading import RLock, Event
from utils import *

#defined by project specification
N = 4
BASE_PORT = 5000
class ReplicaNode(rpyc.Service):
    def __init__(self, my_id):
        self.id = my_id
        self.X = 0
        self.can_write = True if self.id == 1 else False
        self.peer_connections = [BASE_PORT+i for i in range(1,N+1) if i != self.id]
        self.history: List[Tuple[int, int]] = []
        self.W_LOCK = RLock()
        self.permission_granted_event = Event()
        self.DEBUG_MODE = False

    def exposed_read(self):
        return self.X

    def exposed_set(self, value):
        self.W_LOCK.acquire()
        if self.can_write:
            self.__updateX(value)
            self.W_LOCK.release()
        else:
            self.W_LOCK.release()
            
            self.request_write()

            self.permission_granted_event.wait()
            self.permission_granted_event.clear()
            with self.W_LOCK:
                self.__updateX(value)
        
        #async propagate changes
        #respond success

    def __updateX(self, value):
        self.X = value
        self.history.append((self.id, value))

    def set_write(self, primary_id):
        if self.DEBUG_MODE:
            print(f"Permission granted by replica {primary_id}")
        with self.W_LOCK:
            self.can_write = True
            self.permission_granted_event.set()

    def request_write(self):
        #assumes replicas will never fail and will all be available when requested
        for port in self.peer_connections:
            conn = rpyc.connect("localhost", port=port)
            conn.root.ask_for_write_permission(self.set_write)

    def exposed_ask_for_write_permission(self, callback):
        with self.W_LOCK:
            if self.can_write:
                self.can_write = False
                cb = rpyc.async_(callback)
                cb(self.id)

    def exposed_set_debug(self, state):
        self.DEBUG_MODE = state

def node_start(node_instance):
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
    
    local_replica_port = BASE_PORT + replica_id
    
    #setting up replica node
    #logger definition is meant to disable annoying prints made by the RPC lib when the server is interrupted
    replica_node = ThreadedServer(ReplicaNode(replica_id), port=local_replica_port, logger=logging.getLogger().setLevel(logging.CRITICAL))
    replica_process = mp.Process(target=node_start, args=(replica_node,))
    replica_process.start()

    #small delay to allow for the RPC process to fully start before attempting the connection
    time.sleep(0.25)
    replica = rpyc.connect("localhost", port=local_replica_port)
    debug_dict = {"on": True, "off": False}

    print(f"Replica {replica_id} started. Interact with it via the prompt below.")
    print(f"To list the possible commands, type \"help\" or \"?\".")
    #start user interaction loop
    while True:
        try:
            user_input = input("> ")
            user_input = user_input.lower().split(' ')
            command = user_input[0].lower()
            params = user_input[1:]
            param_count = len(params)

        
            if command == "read":
                assert param_count == 0
                value = replica.root.read()
                print(f"X = {value}")
            
            elif command == "history":
                assert param_count == 0
                #TODO: read history from replica
            
            elif command == "set":
                assert param_count == 1
                assert is_int_coercible(params[0])
                value = int(params[0])
                replica.root.set(value)

            elif command == "quit":
                assert param_count == 0
                replica_process.terminate()
                raise KeyboardInterrupt

            elif command in ("help", "?"):
                assert param_count == 0
                #TODO: write well-formatted help text
                print_help()

            elif command == "debug":
                assert param_count == 1
                assert params[0].lower() in ("on", "off")
                replica.root.set_debug(debug_dict.get(params[0].lower()))

            elif command == "":
                continue

            else:
                raise InvalidCommandException

        except AssertionError:
            print(f"Wrong parameters for command '{command}'. Please check instructions by running 'help'.")
        except InvalidCommandException:
            print(f"Command '{command}' is unknown.")
        except KeyboardInterrupt:
            print("Quitting...")
            sys.exit(0)
            
