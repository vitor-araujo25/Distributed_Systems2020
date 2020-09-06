from . import repository

def count_words(file_name):
    text_stream = repository.open(file_name.decode())
    #TODO: write processing code
