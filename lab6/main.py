from utils import *
from config import *
import sys, logging, time, rpyc 
import multiprocessing as mp
from rpyc.utils.server import ThreadedServer
from replica import ReplicaNode

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
    #the protocol config was specified to allow for returning objects in the remote functions
    replica_node = ThreadedServer(ReplicaNode(replica_id), 
                                  port=local_replica_port,
                                  logger=logging.getLogger().setLevel(logging.CRITICAL), 
                                  protocol_config={"allow_public_attrs": True})
    
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
                
            elif command == "history":
                assert param_count == 0
                history_data = replica.root.get_history()
                print_formatted_history(history_data)
            
            elif command == "commit":
                assert param_count == 0
                replica.root.commit_changes()

            elif command == "status":
                assert param_count == 0
                replica_status = replica.root.get_status()
                print_formatted_status_data(replica_status)        

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

            elif command == "quit":
                assert param_count == 0
                raise KeyboardInterrupt
            
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
            
