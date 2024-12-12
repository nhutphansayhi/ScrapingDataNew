from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import asyncio
import os
from client_lib.util import *
from client_lib.connection import *
import sys
import lib
from lib.lib import *
from lib.log import *
import globals
from client_lib.util import *
import json

LOG = lib.LOG
    
def main():
    HOST = globals.SERVER_HOST
    PORT = globals.SERVER_PORT
    BUFSIZ = globals.SERVER_BUFSIZ
    ADDR = (HOST, PORT)
    


if __name__ == "__main__":
    main()