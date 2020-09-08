import ui
import sys

HOST = "127.0.0.1"
PORT = 9000

def main():
    # if len(sys.argv) != 3:
    #     usage
    addr_tuple = (HOST, PORT)
    ui.start(addr_tuple)

if __name__ == "__main__":
    main()