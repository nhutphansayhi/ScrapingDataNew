from Crypto.Random import get_random_bytes
from threading import Thread

input = b'hello'

aes_key = get_random_bytes(16)

def encrypt_packet(packet, key):
    if isinstance(packet, str):
        packet = packet.encode()
    cipher_aes = AES.new(key, AES.MODE_EAX)
    nonce = cipher_aes.nonce
    ciphertext, tag = cipher_aes.encrypt_and_digest(packet)
    return nonce + ciphertext