def is_int_coercible(text):
    try:
        text = int(text)
        return True
    except:
        return False
        
def print_help():
    print(f"help!")
    
def usage():
    print(f"usage: python replica.py ID\n\tID - integer value in the range [1,{N}] containing the id of the replica.")

def print_formatted_history(history):
    print("--------------------------")
    for idx, elem in enumerate(history):
        replica_id, value = elem
        print(f"{idx+1}: Replica {replica_id} -> X = {value}")
    print("--------------------------")
    
class InvalidCommandException(Exception):
    pass