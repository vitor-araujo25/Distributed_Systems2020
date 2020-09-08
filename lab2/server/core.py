import repository
import re
from collections import defaultdict

def count_words(file_name):
    text_stream = repository.open_file_stream(file_name)
    word_dict = defaultdict(int)
    regex = re.compile("\w+")
    for line in text_stream:
        #print(f"DEBUG line: {line}")

        words_in_line = regex.findall(line)
        #print(f"DEBUG words_in_line: {words_in_line}")
        for word in words_in_line:
            word_dict[word.lower()] += 1
    
    return dict(word_dict)


# return {
#     'aaaaa': 10,
#     'bbbb': 5,
#     'ccccc': 20,
#     'ddddd': 30,
#     'eeee': 1,
#     'ffff': 7,
#     'gggg': 8,
#     'hhh': 1,
#     'iii': 2,
#     'jjjj': 5,
#     'hhhh': 1,
#     'mmm': 2,
#     'kkkkkkk': 100,
#     'zzzzzz': 4,
#     'ttttt': 9,
#     'uuuu': 3
# }