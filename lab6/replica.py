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
    def __init__(self, my_id: int):
        self.id = my_id
        self.X = 0
        self.can_write = True if self.id == 1 else False
        self.peer_connections = [BASE_PORT+i for i in range(1,N+1) if i != self.id]
        self.history: List[Tuple[int, int]] = []
        self.uncommitted_history: List[Tuple[int, int]] = []
        self.LOCK = RLock()
        self.permission_granted_event = Event()
        self.DEBUG_MODE = False
        self.changes_committed = True

    def exposed_read(self):
        return self.X
        
    def exposed_set_debug(self, state: bool):
        self.DEBUG_MODE = state

    def exposed_get_history(self):
        return self.history

    def exposed_set(self, value: int):

        BACKOFF_LIMIT = 6

        self.LOCK.acquire()
        if self.can_write:
            debug(self.DEBUG_MODE, "[DEBUG] I have the write token")
            self.__updateX(value)
            self.LOCK.release()
        else:
            self.LOCK.release()
            debug(self.DEBUG_MODE, "[DEBUG] I do not have the write token")
            
            self.request_write()

            #linear backoff on retries 
            #backing off exponentially would not make sense for this use case, as network failures
            #and other interferences are never the cause of delay
            backoff_counter = 0
            interrupted = False
            while not self.permission_granted_event.wait(backoff_counter*0.5):
                if backoff_counter == BACKOFF_LIMIT:
                    interrupted = True
                    break
                self.request_write()
                backoff_counter = backoff_counter + 1 if backoff_counter <= BACKOFF_LIMIT else backoff_counter

            if interrupted:
                return False
            
            with self.LOCK:
                self.permission_granted_event.clear()
                self.__updateX(value)
        
        return True

    def request_write(self):
        #assumes replicas will never fail and will all be available when requested
        #TODO: handle possible errors in a better fashion
        requests_in_flight = []
        debug(self.DEBUG_MODE, "[DEBUG] Trying to get the write token...")
        for port in self.peer_connections:
            conn = rpyc.connect("localhost", port=port)
            ask_for_permission_async = rpyc.async_(conn.root.ask_for_write_permission)
            async_result = ask_for_permission_async()
            async_result.add_callback(self.set_write)
            requests_in_flight.append(async_result)
        [ar.wait() for ar in requests_in_flight]

    def set_write(self, async_result):
        primary_id, had_token, permission_granted = async_result.value
        if had_token:
            debug(self.DEBUG_MODE, f"[DEBUG] Replica {primary_id} had the write token ")
            if permission_granted:
                debug(self.DEBUG_MODE, "and granted it!")
                with self.LOCK:
                    self.can_write = True
                    self.permission_granted_event.set()
            else:
                debug(self.DEBUG_MODE, f"and did not grant it! Mean replica {primary_id}! :(")
    
    def exposed_ask_for_write_permission(self):
        with self.LOCK:
            #check if local changes are committed
            had_token = self.can_write
            if self.can_write and self.changes_committed:
                self.can_write = False
                return (self.id, had_token, True)
            return (self.id, had_token, False)
    
    def exposed_commit_changes(self):
        with self.LOCK:
            if not self.changes_committed:
                self.broadcast_updates()
                self.uncommitted_history = []
                self.changes_committed = True
    
    def broadcast_updates(self):
        #assumes replicas will never fail and will all be available when requested
        #TODO: handle possible errors in a better fashion
        confirmations = [False for peer in self.peer_connections]
        while not all(confirmations):
            requests_in_flight = []

            for i in range(len(self.peer_connections)):
                if confirmations[i] == False:
                    port = self.peer_connections[i]
                    conn = rpyc.connect("localhost", port=port)
                    replicate_changes_async = rpyc.async_(conn.root.replicate_changes)
                    ar_obj = replicate_changes_async(self.id, self.X, self.uncommitted_history)
                    async_request = (i, ar_obj)
                    requests_in_flight.append(async_request)

            for confirmation_id, ar_obj in requests_in_flight:
                confirmations[confirmation_id] = ar_obj.value

    def exposed_replicate_changes(self, primary_id, new_X, new_changes):
        debug(self.DEBUG_MODE, f"[DEBUG] Received push from replica {primary_id} containing value {new_X} as a result of {len(new_changes)}")
        with self.LOCK:
            self.X = new_X
            self.history.extend(new_changes)
        return True

    def __updateX(self, value: int):
        debug(self.DEBUG_MODE, f"[DEBUG] Changing X from {self.X} to {value}")
        self.X = value
        history_entry = (self.id, value)
        self.history.append(history_entry)
        self.uncommitted_history.append(history_entry)
        self.changes_committed = False

def usage():
    print(f"usage: python replica.py ID\n\tID - integer value in the range [1,{N}] containing the id of the replica.")

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
                history_data = replica.root.get_history()
                print_formatted_history(history_data)
            
            elif command == "set":
                assert param_count == 1
                assert is_int_coercible(params[0])
                value = int(params[0])
                while not replica.root.set(value):
                    print("[ERROR] Oops! It seems that we cannot make that update right now. Would you like to try again? [Y/n]: ", end="")
                    opt = input()
                    if opt.lower() in ("", "y"):
                        continue
                    else:
                        break
                else:
                    print(f"Value {value} registered. Send 'commit' to propagate this write or perform other operations.")
            
            elif command == "commit":
                assert param_count == 0
                replica.root.commit_changes()

            elif command == "quit":
                assert param_count == 0
                raise KeyboardInterrupt

            elif command in ("help", "?"):
                assert param_count <= 1
                try:
                    help_command = params[0]
                    command = help_command  #quick fix for printing the consulted command if it doesn't exist
                except IndexError:
                    help_command = None
                print_help(help_command)

            elif command == "debug":
                assert param_count == 1
                assert params[0].lower() in ("on", "off")
                replica.root.set_debug(debug_dict.get(params[0].lower()))
                print(f"[DEBUG MODE IS {params[0].upper()}]")

            elif command == "":
                continue

            else:
                raise InvalidCommandException

        except AssertionError:
            print(f"Wrong parameters for command '{command}'. Please check instructions by running 'help {command}'.")
        except InvalidCommandException:
            print(f"Command '{command}' is unknown.")
        except (KeyboardInterrupt, EOFError):
            print("\nQuitting...")
            replica_process.terminate()
            sys.exit(0)
            
