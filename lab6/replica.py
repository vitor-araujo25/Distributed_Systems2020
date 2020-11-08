#!/usr/bin/python
import rpyc, sys
from rpyc.utils.server import ThreadedServer

class ReplicaNode(rpyc.Service):
    pass

def usage():
    print("usage: python replica.py ID\n\tID - integer value in the range [1,4] containing the id of the replica.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong parameter count.")
        usage()
        sys.exit(1)
    try:
        replica_id = int(sys.argv[1])
        if replica_id > 4 or replica_id < 1:
            raise ValueError
    except (TypeError, ValueError):
        print("ID parameter must be an integer in the range [1,4]!")
        usage()
        sys.exit(1)
    

    #start replica server