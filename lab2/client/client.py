import ui
import sys
import socket

HOST = "127.0.0.1"
PORT = 9000

def main():
    if len(sys.argv) != 3:
        usage()
    addr_tuple = (HOST, PORT)
    start(addr_tuple)

def start(remote_addr):
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)

    with sock as s:
        try:
            s.connect(remote_addr)
            conn = s.getpeername()
            print(f"Connected to {conn[0]}:{conn[1]} successfully.")
            ui.interaction_loop(s)

        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception as e:
            print(f"Uncaught exception raised inside UI loop: {e}")
        finally:
            print("\nEnding connection...")
            sock.sendall(b"CLOSE")

def usage():
    print("Wrong parameters!")
    sys.exit(1)

if __name__ == "__main__":
    main()