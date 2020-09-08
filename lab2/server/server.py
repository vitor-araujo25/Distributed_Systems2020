import gateway, configs

def main():
    print("Starting server")
    addr = (configs.HOST, configs.PORT)
    gateway.start(addr)

if __name__ == "__main__":
    main()