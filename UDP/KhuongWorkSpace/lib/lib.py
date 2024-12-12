from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import hashlib
from Crypto.Util.number import bytes_to_long, long_to_bytes
import os


def ip_to_bytes(ip):
    if ip == 'localhost':
        ip = '127.0.0.1'
    return bytes(map(int, ip.split('.')))

def int_to_ip(n):
    return inet_ntoa(n.to_bytes(4, byteorder='big'))



def fill_zero(data, n):
    if len(data) < n:
        # Thêm byte 0 vào cuối để đủ n bytes
        data = data.ljust(n, b'\0')
    return data


def create_packet(data, ip, port, type, connection, AES_KEY):
    
    # print(ip, port)
    protocol_name = b'GEYS'  # Định dạng protocol name (4 byte)
    sender_ip = fill_zero(ip_to_bytes(ip), 4)  # Địa chỉ IP (4 byte)
    sender_port = long_to_bytes(port, 2)  # Port (2 byte)
    type_request = type.encode('utf-8')[:1]  # Loại request (1 byte)
    content = data if isinstance(data, bytes) == True else data.encode('utf-8')  # Nội dung (n bytes)
    encrypted_content = encrypt_packet(content, AES_KEY)
    content_length = long_to_bytes(len(encrypted_content), 4)  # Độ dài nội dung (4 byte)
    encrypted_header = encrypt_packet(protocol_name + sender_ip + sender_port + type_request + content_length, AES_KEY)
   
    # Tạo gói tin
    packet = encrypted_header + encrypted_content
    return packet

def calculate_hash_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:  # Mở tệp ở chế độ đọc nhị phân
            while chunk := f.read(8192):  # Đọc tệp theo từng khối (8192 byte mỗi lần)
                sha256_hash.update(chunk)  # Cập nhật hash với khối dữ liệu
        return {'sum': sha256_hash.hexdigest(), 'code': 0}  # Trả về mã hash dạng chuỗi hex
    except FileNotFoundError:
        return {'sum': '', 'code': -1}  # Trả về mã hash rỗng nếu không tìm thấy tệp
    except Exception as e:
        return {'sum': '', 'code': -2}  # Trả về mã hash rỗng nếu có lỗi xảy ra

def decrypt_packet(packet, key):
    nonce = packet[:16]
    cipher_aes = AES.new(key, AES.MODE_EAX, nonce=nonce)
    ciphertext = packet[16:]
    plaintext = cipher_aes.decrypt(ciphertext)
    return plaintext

def encrypt_packet(packet, key):
    if isinstance(packet, str):
        packet = packet.encode()
    cipher_aes = AES.new(key, AES.MODE_EAX)
    nonce = cipher_aes.nonce
    ciphertext, tag = cipher_aes.encrypt_and_digest(packet)
    return nonce + ciphertext

def GEYS_header_parse(header):
    protocol_name = header[:4].decode('utf-8')
    sender_ip = bytes_to_long(header[4:8])
    sender_port = int.from_bytes(header[8:10], byteorder='big')
    type_request = header[10:11].decode('utf-8')
    content_length = int.from_bytes(header[11:15], byteorder='big')
    return protocol_name, sender_ip, sender_port, type_request, content_length


def GEYS_parse(packet):
    header = packet[:15]
    protocol_name, sender_ip, sender_port, type_request, content_length = GEYS_header_parse(header)
    content = packet[15:content_length+15]
    return protocol_name, sender_ip, sender_port, type_request, content_length, content
