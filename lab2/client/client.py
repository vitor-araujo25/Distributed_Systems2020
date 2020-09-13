import sys, socket
import ui

HOST = "127.0.0.1"
PORT = 9000

def main():
    # if len(sys.argv) != 3:
    #     usage
    addr_tuple = (HOST, PORT)
    start(addr_tuple)

def start(remote_addr):
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)

    with sock as s:
        s.connect(remote_addr)
        conn = s.getpeername()
        print(f"Connected to {conn[0]}:{conn[1]} successfully.")
        try:
            ui.interaction_loop(s)
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception as e:
            print(f"Uncaught exception raised inside UI loop: {e}")
        finally:
            print("\nEnding connection...")

if __name__ == "__main__":
    main()