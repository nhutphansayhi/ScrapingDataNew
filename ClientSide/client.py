from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import asyncio
import os
from ClientLib.clientlib import handle_process
import sys

sys.path.append('../Lib/') 

from lib import decrypt_packet

HOST = "localhost"
PORT = 3000
    
async def main():

    c = socket(AF_INET, SOCK_STREAM)
    c.connect((HOST, PORT))

    # Nhận khóa công khai RSA từ server
    public_key = c.recv(450)
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(public_key))

    # Tạo khóa AES và mã hóa bằng khóa công khai RSA của server
    aes_key = get_random_bytes(16)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)
    c.send(encrypted_aes_key)
    # print("AES key generated and sent.")
    
    files = c.recv(1024)
    print("Files in server directory:")
    print(decrypt_packet(files, aes_key).decode())

    try:
        pass
        # while True:
        #     await handle_process(c, aes_key)
    except KeyboardInterrupt:
        print("Client stopped.")
    finally:
        c.close()
        
asyncio.run(main())