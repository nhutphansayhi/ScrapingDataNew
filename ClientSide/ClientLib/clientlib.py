from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import asyncio

async def handle_process(c, aes_key, public_key):
    data = input("Enter message: ")
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    encrypted_data = cipher_aes.nonce + cipher_aes.encrypt(data.encode())
    c.send(encrypted_data)
    
    # Nhận phản hồi đã mã hóa từ server
    encrypted_response = c.recv(1024)
    if not encrypted_response:
        return
    
    