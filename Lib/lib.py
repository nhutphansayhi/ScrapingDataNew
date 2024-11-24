from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import asyncio
import os

def decrypt_packet(packet, key):
    nonce = packet[:16]
    ciphertext = packet[16:]
    cipher_aes = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = cipher_aes.decrypt(ciphertext)
    return data.decode()
