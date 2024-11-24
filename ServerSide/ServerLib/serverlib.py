from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import asyncio
import os

def getFiles(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return files

async def handle_client(c, a, public_key, private_key):
    
    print("Connection from: ", a)
    # Gửi khóa công khai RSA cho client
    c.send(public_key)
    
    # Nhận khóa AES đã mã hóa từ client
    encrypted_aes_key = c.recv(256)
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(private_key))
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)
    
    # print("AES key received and decrypted.")
    
    fileList = str(getFiles('Database'))
    print(fileList)
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    encrypted_file = cipher_aes.nonce + cipher_aes.encrypt(fileList.encode())
    c.send(encrypted_file)
    
    
    # while True:
    #     # Nhận dữ liệu đã mã hóa từ client
    #     encrypted_data = c.recv(1024)
    #     if not encrypted_data:
    #         break
        
    #     # Giải mã dữ liệu bằng AES
    #     nonce = encrypted_data[:16]
    #     ciphertext = encrypted_data[16:]
    #     cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
    #     data = cipher_aes.decrypt(ciphertext)
    #     print("Decrypted data:", data.decode())
        
    #     # Nhập phản hồi và mã hóa bằng AES
    #     response = input("Enter response: ")
    #     cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    #     encrypted_response = cipher_aes.nonce + cipher_aes.encrypt(response.encode())
    #     c.send(encrypted_response)
        
