from socket import *
import server_lib
from server_lib.util import *
from threading import Thread
import sys
import globals
from server_lib.connection import *
from server_lib.util import *
import lib

LOG = lib.LOG

addresses = {}

def main():
    
    HOST = globals.SERVER_HOST
    PORT = globals.SERVER_PORT
    BUFSIZ = globals.SERVER_BUFSIZ
    ADDR = (HOST, PORT)
    

        
if __name__ == "__main__":
    main()
