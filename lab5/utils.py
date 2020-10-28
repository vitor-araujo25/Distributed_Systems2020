import hashlib 

def sha(key: str):
    return int(hashlib.sha1(str(key).encode()).hexdigest(), 16)

class NodeID(object):

    def __init__(self, node_id, port):
        self.node_id = node_id
        self.port = port

    def __repr__(self):
        return f"[{self.node_id}] --> localhost:{self.port}"