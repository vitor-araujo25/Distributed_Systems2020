import hashlib 

def hash(key: str):
    return int(hashlib.sha1(str(key).encode()).hexdigest(), 16)