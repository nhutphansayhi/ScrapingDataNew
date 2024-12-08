from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import asyncio
import os
from TCP.client_lib.util import *
from TCP.client_lib.connection import *
import sys
import TCP.lib
from TCP.lib.lib import *
from TCP.lib.log import *
import TCP.globals
from TCP.client_lib.util import *
import json

LOG = lib.LOG
    
def main():
    HOST = globals.SERVER_HOST
    PORT = globals.SERVER_PORT
    
    c = socket(AF_INET, SOCK_STREAM)
    c.connect((HOST, PORT))
    AES_KEY = handshake(c)
    
    client_ip, client_port = c.getsockname()
    files_list = getFileList(c, client_ip, client_port, AES_KEY)
    
    files_list = json.loads(files_list['data'].decode('utf-8'))

    msg_files_list = "[magenta]Files in server database:[/magenta]\n" + "\n".join([f"[green]{f['name']}[/green] - {f['size'] // (1024**2) } MB" for f in files_list])
    LOG.info(msg_files_list, extra={"markup": True})

    handle_process(c, client_ip, client_port, AES_KEY)
    
    
    c.close()        

if __name__ == "__main__":
    main()