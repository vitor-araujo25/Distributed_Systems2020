def open(file_name):
    with open(file_name) as f:
        yield from f.readline()