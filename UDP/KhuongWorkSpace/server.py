from threading import Thread
import sys
import TCP.globals
from TCP.server_lib.connection import *
from TCP.server_lib.util import *
import TCP.lib

LOG = lib.LOG

addresses = {}

def main():
    HOST = globals.SERVER_HOST
    PORT = globals.SERVER_PORT
    BUFSIZ = globals.SERVER_BUFSIZ
    ADDR = (HOST, PORT)
    try:
        SERVER = socket(AF_INET, SOCK_DGRAM)
        SERVER.bind(ADDR)
        LOG.info("Server started.")
        LOG.info(f"Server listening on {HOST}:{PORT}")
        LOG.info("Waiting for messages...")
        while True:
            try:
                data, client_address = SERVER.recvfrom(BUFSIZ)
                LOG.info(f"Received message from {client_address}")
                # Handle the received data
                handle_message(data, client_address, SERVER)
            except KeyboardInterrupt:
                LOG.info("Server stopped.")
                break
            except Exception as e:
                LOG.error(f"Error: {e}")
    finally:
        SERVER.close()

def handle_message(data, client_address, server, public_key, private_key):
    # Implement your message handling logic here
    pass

if __name__ == "__main__":
    main()