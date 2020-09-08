import socket
import json

def interaction_loop(sock):
    while True:
        ALL_MESSAGES_COLLECTED = False
        file_name = input("Type the file name: ")
        if file_name == "":
            break
        sock.sendall(file_name.encode())

        #starting message collection loop
        #If server response is larger than 1024 bytes, segmentation will occur,
        #in which case, this loop will iterate until msg_buf has a valid JSON object
        msg_buf = ""
        while not ALL_MESSAGES_COLLECTED:
            response_json = sock.recv(1024)
            response_json = response_json.decode()
            if response_json == "ERROR":
                print("The file you chose appears to not exist. Try again.")
                break
            try:
                msg_buf += response_json
                word_list = json.loads(msg_buf)
            except json.JSONDecodeError:
                continue
            else:
                ALL_MESSAGES_COLLECTED = True         
        else: 
            #this block will only execute if the while loop 
            #exited successfully (not via break call)      
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
