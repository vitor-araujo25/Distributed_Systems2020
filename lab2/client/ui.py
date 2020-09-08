import socket
import json

def interaction_loop(sock):
    ALL_MESSAGES_COLLECTED = False

    while True:
        file_name = input("Type the file name: ")
        if file_name == "":
            break
        sock.sendall(file_name.encode())

        msg_buf = ""
        while not ALL_MESSAGES_COLLECTED:
            response_json = sock.recv(1024)
            #print(f"DEBUG: msg received: {response_json.decode()}")
            if response_json.decode() == "ERRO":
                print("The file you chose appears to not exist. Try again.")
                break
            try:
                msg_buf += response_json.decode('utf-8')
                word_list = json.loads(msg_buf)
            except json.JSONDecodeError:
                continue
            else:
                ALL_MESSAGES_COLLECTED = True         
        else:       
            filtered_word_list = process_word_list(word_list)
            render(filtered_word_list, file_name)
        
def process_word_list(word_list):
    '''
    Sorts all words from word_list by descending order of frequency (value)
    and returns the top 10 from that sorted list.
    '''
    words = list(word_list.items())
    words.sort(key=lambda tup: tup[1], reverse=True)
    return {word: count for word, count in words[:10]}

def render(word_count, file_name):
    print()
    print(f"Most frequent words in file '{file_name}':")
    print("----------------------------------------------")
    for word, count in word_count.items():
        print(f"  '{word}' --> {count} occurences")
    print("----------------------------------------------")
    print()
