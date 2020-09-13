import re
from collections import defaultdict
import repository

def count_words(file_name):

    #Calling data access layer (repository) to open file.
    #Raises OSError if file is nonexistent.
    text_stream = repository.open_file_stream(file_name)

    #Dictionary in which every new key automatically has value = 0
    word_dict = defaultdict(int)

    #Regex to isolate every word in a text string
    #Considers compound words (i.e. from the portuguese language) as
    #well as contracted expressions from english as a single word
    regex = re.compile("[\w\-']+")

    for line in text_stream:
        #applies the regex and wraps the resulting words in a list
        words_in_line = regex.findall(line)
        for word in words_in_line:
            word_dict[word.lower()] += 1
    
    return dict(word_dict)
