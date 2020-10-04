import sys, socket
import ui, configs


def main():
    # if len(sys.argv) != 3:
    #     usage
    addr_tuple = (configs.SERVER_IP, configs.SERVER_PORT)
    start(addr_tuple)

def start(remote_addr):
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)

    with sock as s:
        s.connect(remote_addr)
        print(f"Connected to server successfully.")
        try:
            ui.interaction_loop(s)
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception as e:
            print(f"Uncaught exception raised inside the UI loop: {e}")
        finally:
            print("\nEnding connection...")
            #TODO: Enviar msg de "goodbye"

if __name__ == "__main__":
    main()