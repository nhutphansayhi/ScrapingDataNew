from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import asyncio
from ServerLib.serverlib import handle_client

HOST = "localhost"
PORT = 3000

# Tạo cặp khóa RSA
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

    
async def main():
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)

    print(f"Server running on {HOST}:{PORT}")
    try:
        while True:
            c, a = s.accept()
            await handle_client(c, a, public_key, private_key)
            c.close()
    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        s.close()
asyncio.run(main())