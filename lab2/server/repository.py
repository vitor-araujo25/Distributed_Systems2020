from pathlib import Path

local_file_folder = Path(__file__).parent.absolute() / "files"

def open_file_stream(file_name):
    with open(local_file_folder / file_name, encoding='utf-8') as f:
        yield from f.readlines()