import socket
import os
import threading
import hashlib

def calculate_checksum(data):
    return hashlib.md5(data).hexdigest()

def handle_client(sock, addr):
    print(f"Connected to {addr}")
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            if not data:
                break
            request = data.decode().split()
            if request[0] == "LIST":
                send_file_list(sock, addr)
            elif len(request) == 2:
                filename, offset = request
                offset = int(offset)
                file_path = os.path.join("database", filename)
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        f.seek(offset)
                        seq_num = 0
                        while True:
                            chunk = f.read(4096 - 10)
                            if not chunk:
                                break
                            checksum = calculate_checksum(chunk)
                            packet = f"{seq_num}|{checksum}".encode() + b'|' + chunk
                            sock.sendto(packet, addr)
                            try:
                                ack, _ = sock.recvfrom(1024)
                                ack_num = int(ack.decode())
                                if ack_num == seq_num:
                                    seq_num += 1
                                else:
                                    f.seek(offset + seq_num * (4096 - 10))
                            except socket.timeout:
                                f.seek(offset + seq_num * (4096 - 10))
                        sock.sendto(b'EOF', addr)
                    print(f"File {filename} sent successfully from offset {offset}")
                else:
                    sock.sendto(b'ERROR: File not found', addr)
            else:
                sock.sendto(b'ERROR: Invalid request', addr)
        except socket.timeout:
            continue

def send_file_list(sock, addr):
    files = os.listdir("database")
    file_list = "\n".join(files)
    sock.sendto(file_list.encode(), addr)

def udp_file_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.settimeout(1)
    print(f"Server listening on {host}:{port}")

    while True:
        try:
            data, addr = sock.recvfrom(2048)
            threading.Thread(target=handle_client, args=(sock, addr)).start()
        except socket.timeout:
            print("Server is still alive")
            continue

if __name__ == "__main__":
    udp_file_server('localhost', 54321)