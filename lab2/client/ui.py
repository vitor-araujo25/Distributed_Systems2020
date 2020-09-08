import socket
import json

FULL_WORD_DICT = {}
ALL_MESSAGES_COLLECTED = False

def interaction_loop(sock):
    restore_vars()

    while True:
        file_name = input("Type the file name: ")
        if file_name == "":
            break
        sock.sendall(file_name.encode())

        while not ALL_MESSAGES_COLLECTED:
            response_json = sock.recv(2048)
            try:
                collect(response_json)
            except:
                print(f"An error occurred when decoding message from server. Try again.")
                break           
        else:       
            filtered_word_list = process_full_word_dict()
            render(filtered_word_list, file_name)
        restore_vars()
        
def restore_vars():
    FULL_WORD_DICT = {}
    ALL_MESSAGES_COLLECTED = False

def collect(word_list):
    partial_word_dict = json.loads(word_list)
    FULL_WORD_DICT.update(partial_word_dict['words'])
    
    #when more_items field has value 'false', no more messages will be sent and
    #FULL_WORD_DICT is ready to be filtered and ordered
    if not partial_word_dict['more_items']:
        ALL_MESSAGES_COLLECTED = True

def process_full_word_dict():
    words = FULL_WORD_DICT.items()
    words.sort(key=lambda tup: tup[1], reverse=True)
    return {word: count for word, count in words[:10]}

def render(word_count, file_name):
    print()
    print(f"Most frequent words in file '{file_name}':")
    print("----------------------------------------------")
    for word, count in word_count:
        print(f"  '{word}' --> {count} occurences")
    print("----------------------------------------------")
    print()
