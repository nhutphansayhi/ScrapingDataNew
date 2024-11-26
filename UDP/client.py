import socket
import os
import threading
import time

# Đọc danh sách file từ input.txt
def read_input_file():
    with open('input.txt', 'r') as file:
        return file.readlines()

# Hàm tải chunk file từ server
def download_chunk(file_name, chunk_start, chunk_size, client_socket):
    request = f"{file_name},{chunk_start},{chunk_size}"
    client_socket.send(request.encode())

    chunk_data = client_socket.recv(chunk_size)
    with open(file_name, 'ab') as file:
        file.write(chunk_data)
    
    print(f"Downloaded {file_name} chunk {chunk_start}-{chunk_start + chunk_size - 1}")

# Hàm tải file với 4 kết nối song song
def download_file(file_name, total_size):
    chunk_size = total_size // 4  # Chia đều thành 4 phần
    threads = []
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('127.0.0.1', 12345))  # Kết nối tới server

        # Tạo 4 kết nối song song để tải file
        for i in range(4):
            chunk_start = i * chunk_size
            thread = threading.Thread(target=download_chunk, args=(file_name, chunk_start, chunk_size, client_socket))
            threads.append(thread)
            thread.start()

        # Chờ tất cả các threads hoàn thành
        for thread in threads:
            thread.join()

# Hàm main của client
def start_client():
    while True:
        file_list = read_input_file()
        for file_name in file_list:
            file_name = file_name.strip()
            if os.path.exists(file_name):
                print(f"{file_name} already downloaded")
            else:
                print(f"Starting to download {file_name}")
                download_file(file_name, 1000000)  # Giả sử 1000000 là tổng dung lượng file (sử dụng giá trị thực tế ở đây)
                print(f"Download of {file_name} completed.")

        time.sleep(5)  # Đọc lại input.txt sau 5 giây

if __name__ == "__main__":
    start_client()