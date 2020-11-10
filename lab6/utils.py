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
    elif command == "commit":
        print("commit \n\tPropagates the changes performed locally to all the replicas. \n\tIf any writes were performed locally, other replicas will not be able to perform \n\ttheir writes until this command is issued, so be mindful of it.\n")
    elif command == "status":
        print("status \n\tPrints information about the current inner state of the local replica.\n")
    elif command == "help" or command == "?":
        print("help [command]\n? [command] \n\ttype(command): string \n\tReturn: Instructions for the given command. If none was given, prints help for all commands.\n")
    elif command == "debug":
        print("debug off|on \n\tReturn: None \n\tEnables/disables debug messages.\n")
    elif command == "quit":
        print("quit \n\tReturn: None \n\tFinishes the application.\n")
    elif command == None:
        print("read \n\tReturn: Current value of X.\n")
        print("set <value> \n\ttype(value): int \n\tSets the current value of X equal to 'value'.\n")
        print("history \n\tReturn: Ordered list of changes performed to the variable X, identified by replicas.\n")
        print("commit \n\tPropagates the changes performed locally to all the replicas. \n\tIf any writes were performed locally, other replicas will not be able to perform \n\ttheir writes until this command is issued, so be mindful of it.\n")
        print("status \n\tPrints information about the current inner state of the local replica.\n")
        print("help [command]\n? [command] \n\ttype(command): string \n\tPrints instructions for the given command. \n\tIf none was given, prints help for all commands.\n")
        print("debug off|on \n\tReturn: None \n\tEnables/disables debug messages.\n")
        print("quit \n\tReturn: None \n\tFinishes the application.\n")
    else:
        raise InvalidCommandException

def print_formatted_history(history):
    print("---------------------------")
    for idx, elem in enumerate(history):
        replica_id, value = elem
        print(f"{idx+1}: Replica {replica_id} -> X = {value}")
    print("---------------------------")

def print_formatted_status_data(status_data):
    print("---------------------------")
    for k,v in status_data.items():
        print(f"{k}: {v}")
    print("---------------------------")

def debug(debug_on, *args, **kwargs):
    if debug_on:
        # print("") #inserting newline
        print(*args, **kwargs)
    
class InvalidCommandException(Exception):
    pass