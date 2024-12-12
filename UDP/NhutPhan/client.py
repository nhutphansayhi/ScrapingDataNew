import socket
import threading
import os
import time
import hashlib

def calculate_checksum(data):
    return hashlib.md5(data).hexdigest()

def download_chunk(host, port, filename, offset, part_num, total_size, progress):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    request = f"{filename} {offset}"
    sock.sendto(request.encode(), (host, port))

    with open(f"{filename}.part{part_num}", 'wb') as f:
        expected_seq_num = 0
        while True:
            try:
                data, _ = sock.recvfrom(4096)
                if data == b'EOF':
                    break
                if b'|' in data:
                    header, chunk = data.split(b'|', 1)
                    seq_num, checksum = header.decode().split('|')
                    seq_num = int(seq_num)
                    if seq_num == expected_seq_num and calculate_checksum(chunk) == checksum:
                        f.write(chunk)
                        sock.sendto(str(seq_num).encode(), (host, port))
                        progress[part_num] += len(chunk)
                        print_progress(filename, progress, total_size)
                        expected_seq_num += 1
                    else:
                        sock.sendto(str(expected_seq_num - 1).encode(), (host, port))
                else:
                    sock.sendto(str(expected_seq_num - 1).encode(), (host, port))
            except socket.timeout:
                sock.sendto(str(expected_seq_num - 1).encode(), (host, port))

def print_progress(filename, progress, total_size):
    total_downloaded = sum(progress)
    percent = (total_downloaded / total_size) * 100
    print(f"Downloading {filename} .... {percent:.2f}%")

def download_file(host, port, filename, file_size):
    total_size = int(float(file_size[:-2]) * 1024 * 1024)
    chunk_size = total_size // 4
    progress = [0] * 4

    threads = []
    for i in range(4):
        offset = i * chunk_size
        t = threading.Thread(target=download_chunk, args=(host, port, filename, offset, i, total_size, progress))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    with open(filename, 'wb') as f:
        for i in range(4):
            part_file = f"{filename}.part{i}"
            with open(part_file, 'rb') as pf:
                f.write(pf.read())
            os.remove(part_file)

def read_input_file(input_file):
    with open(input_file, 'r') as f:
        return [line.strip() for line in f.readlines()]

def receive_file_list(sock):
    data, _ = sock.recvfrom(4096)
    file_list = data.decode().split('\n')
    print("Available files:")
    for file in file_list:
        print(file)

def udp_file_client(host, port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b'LIST', (host, port))
    receive_file_list(sock)
    downloaded_files = set()
    while True:
        files_to_download = read_input_file(input_file)
        new_files = [f for f in files_to_download if f not in downloaded_files]
        for file in new_files:
            filename, file_size = file.split()
            download_file(host, port, filename, file_size)
            downloaded_files.add(file)
        time.sleep(5)

if __name__ == "__main__":
    udp_file_client('localhost', 54321, 'input.txt')