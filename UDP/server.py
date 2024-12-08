import socket
import os
import threading

# Hàm gửi file cho client
def send_file_chunk(client_socket, file_name, chunk_start, chunk_size):
    try:
        with open(file_name, 'rb') as file:
            file.seek(chunk_start)
            chunk_data = file.read(chunk_size)
            client_socket.send(chunk_data)
    except Exception as e:
        print(f"Error sending file chunk: {e}")

# Hàm phục vụ client
def handle_client(client_socket):
    try:
        # Nhận yêu cầu download file từ client
        file_request = client_socket.recv(1024).decode()
        file_name, chunk_start, chunk_size = file_request.split(',')
        chunk_start = int(chunk_start)
        chunk_size = int(chunk_size)

        if os.path.exists(file_name):
            send_file_chunk(client_socket, file_name, chunk_start, chunk_size)
        else:
            client_socket.send(b"File not found")
    except Exception as e:
        print(f"Error handling client request: {e}")
    finally:
        client_socket.close()

# Hàm main của server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(5)
    print("Server listening on port 12345...")
    
    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()