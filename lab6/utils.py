def is_int_coercible(text):
    try:
        text = int(text)
        return True
    except:
        return False
        
def print_help(command=None):
    if command == "read":
        print("read \n\tReturn: Current value of X.\n")
    elif command == "set":
        print("set <value> \n\ttype(value): int \n\tSets the current value of X equal to 'value'.\n")
    elif command == "history":
        print("history \n\tReturn: Ordered list of changes performed to the variable X, identified by replicas.\n")
    elif command == "help" or command == "?":
        print("help [command]\n? [command] \n\ttype(command): string \n\tReturn: Instructions for the given command. If none was given, prints help for all commands.\n")
    elif command == "quit":
        print("quit \n\tReturn: None \n\tFinishes the application.\n")
    elif command == "debug":
        print("debug off|on \n\tReturn: None \n\tEnables/disables debug messages.\n")
    elif command == None:
        print("read \n\tReturn: Current value of X.\n")
        print("set <value> \n\ttype(value): int \n\tSets the current value of X equal to 'value'.\n")
        print("history \n\tReturn: Ordered list of changes performed to the variable X, identified by replicas.\n")
        print("help [command]\n? [command] \n\ttype(command): string \n\tReturn: Instructions for the given command. If none was given, prints help for all commands.\n")
        print("quit \n\tReturn: None \n\tFinishes the application.\n")
        print("debug off|on \n\tReturn: None \n\tEnables/disables debug messages.\n")
    else:
        raise InvalidCommandException

def print_formatted_history(history):
    print("-----------------------------------")
    for idx, elem in enumerate(history):
        replica_id, value = elem
        print(f"{idx+1}: Replica {replica_id} -> X = {value}")
    print("-----------------------------------")

def debug(debug_on, *args, **kwargs):
    if debug_on:
        print(*args, **kwargs)
    
class InvalidCommandException(Exception):
    pass