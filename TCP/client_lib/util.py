from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from threading import Thread
import lib
from lib.lib import *
import globals
from rich.progress import Spinner
import time
from rich.progress import Progress
import hashlib
import os
import sys
import time
import json
from client_lib.connection import *
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
directory = ''
CHUNK_NUMBER = globals.CHUNK_NUMBER


        

def merge_file(file_name):
    file_path = os.path.join("download", file_name)
    with open(file_path, 'wb') as f:
        for i in range(CHUNK_NUMBER):
            chunk_path = os.path.join("download", file_name + f".part{i+1}")
            with open(chunk_path, 'rb') as chunk_f:
                f.write(chunk_f.read())
            os.remove(chunk_path)

def download_chunk(file_name, offset, length, chunk_index, progress, task_id):
    LOG = lib.LOG
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((globals.SERVER_HOST, globals.SERVER_PORT))
    dc_aes_key = handshake(client)
    client_ip, client_port = client.getsockname()
    payload = {
        'file_name': file_name,
        'offset': offset,
        'length': length,
        'chunk_index': chunk_index
    }

    client.settimeout(5)
    client.sendall(create_packet(json.dumps(payload), client_ip, client_port, 'D', client, dc_aes_key))
    download_path = os.path.join("download", file_name + f".part{chunk_index}")
    # try:
    with open(download_path, 'wb') as f:
        chunk_downloaded = 0
        while True:
            header = client.recv(15+16)
            header = decrypt_packet(header, dc_aes_key)
            protocol_name, sender_ip, sender_port, type_request, payload_length = GEYS_header_parse(header)
            data = client.recv(payload_length)
            data = decrypt_packet(data, dc_aes_key)
            if(data == b'EOF'):
                # LOG.info(f"{data}")
                break
            chunk_downloaded = len(data)
            
            f.write(data)
            # LOG.info(chunk_downloaded)
            client.sendall(create_packet("ACK", client_ip, client_port, 'A', client, dc_aes_key))
            
            progress.update(task_id, advance=chunk_downloaded)
    disconnect(client, client_ip, client_port, dc_aes_key)
    return 1
    # except Exception as e:
    #     LOG.error(f"Error: {e}")
    #     return -1

def download_file(connection, client_ip, client_port, file_name, aes_key):
    LOG = lib.LOG
    # print('send ', create_packet(file_name, 'D', connection))
    payload = {
        'file_name': file_name,
        'chunk_number': CHUNK_NUMBER
    }
    # time.sleep(3)
    connection.settimeout(5)
    connection.sendall(create_packet(json.dumps(payload), client_ip, client_port, 'E',  connection, aes_key))
    # LOG.info("lll")
    # connection.send(create_packet(file_name, 'D', connection))
    try:
        data = connection.recv(16+15)
        data = decrypt_packet(data, aes_key)
        protocol_name, sender_ip, sender_port, type_request, payload_length = GEYS_header_parse(data)
        payload = connection.recv(payload_length) 
        payload = decrypt_packet(payload, aes_key)
        payload = json.loads(payload.decode())
        response = payload['response']
        if response == 'N':
            raise Exception('File not found')
        threads = []
        file_size = payload['file_size']
    
        LOG.info(f"[cyan]Downloading file: [green]{file_name}[/] - {file_size // (2**20)} MB[/cyan]", extra={"markup": True})   
        # LOG.info(f"     File size: {file_size}")
        chunk_size = (file_size + CHUNK_NUMBER - 1) // CHUNK_NUMBER
        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            
            TimeRemainingColumn(),
        )
        with progress:
            tasks_id = []
            for i in range(CHUNK_NUMBER):
                offset = chunk_size * i
                length = min(chunk_size, file_size - offset)
                task_id = progress.add_task(f"Part {i+1}", total=length)
                tasks_id.append(task_id)
                thr = Thread(target=download_chunk, args=(file_name, offset, length, i+1, progress, task_id))
                thr.start()
                threads.append(thr)
            
            for thr in threads:
                thr.join()
            merge_file(file_name)
        return 1
        
        # CHUNK_NUMBER = globals.CHUNK_NUMBER
        # threads = [
        #     Thread(target=download_chunk, args=(file_name, offset, i))
        #     for i in range(CHUNK_NUMBER)
        # ]
        # tasks = [
        #     {"desc": f"Downloading chunk {i+1}", "duration": 1}
        #     for i in range(CHUNK_NUMBER)
        # ]
        # task_ids = [
        #     progress.add_task(task["desc"], total=100) for task in tasks
        # ]
    except Exception as e:
        LOG.error(f"Error: {e}")
        return -1
        
def msg_found_file(files_list):
    if len(files_list) == 0:
        return '[magenta]No file found in your input.txt[/]'
    msg = '[magenta]Found file in your input.txt:[/]\n'
    for i in range(len(files_list)):
        msg = msg + f'{i+1}. [green]{files_list[i]}[/]\n'
    return msg

def getFirstChecking(file_path):
    files_list = []
    line = 0
    with open(file_path, 'r') as f:
        files = f.readlines()
        for file in files:
            line += 1
            file = file.strip()
            files_list.append(file)
    return files_list, line

def detect_file_change(file_path, current_line, sha256):
    files_list = []
    new_sha256 = calculate_hash_sha256(file_path)
    if new_sha256 != sha256:
        new_files_list, new_current_line = getFirstChecking(file_path)
        files_list = new_files_list[current_line:]
        current_line = new_current_line
    return files_list, current_line, new_sha256

def handle_process(connection, client_ip, client_port, aes_key):
    LOG = lib.LOG
    CONSOLE = lib.CONSOLE
    # try:
    # while True:
    files_list = []
    current_line = 0
    sha256 = -1
    with CONSOLE.status("[cyan]First checking your input.txt...") as status:
        spinner = Spinner("circle")
        file_path = os.path.join(directory, 'input.txt')
        # print(file_path)
        sha256 = calculate_hash_sha256(file_path)
        files_list, current_line = getFirstChecking(file_path)
        time.sleep(2)

    LOG.info(msg_found_file(files_list), extra={"markup": True})
    # disconnect(connection, client_ip, client_port, aes_key)
    while True:
        if len(files_list):
            LOG.info("[cyan]Found changes in your input.txt:[/]", extra={"markup": True})
            for file in files_list:
                LOG.info(f"  [green]{file}[/]", extra={"markup": True})
            LOG.info("[cyan]Starting download files...[/]", extra={"markup": True})
            for i in range(len(files_list)):
                file_name = files_list[i]
                response = download_file(connection, client_ip, client_port, file_name, aes_key)
                if response == 1:
                    LOG.info(f"[green]Downloaded file {file_name} successfully[/]", extra={"markup": True})
        else:
            LOG.info("[cyan]No file found in your input.txt. Waiting for changes...[/]", extra={"markup": True})
        time.sleep(5)
        files_list, current_line, sha256 = detect_file_change(file_path, current_line, sha256) 
    
    # disconnect(connection, client_ip, client_port, aes_key)
    
        # with CONSOLE.status("[cyan]Scanning changes in your input.txt...") as status:
        #     spinner = Spinner("circle")  # Chọn loại spinner, có thể là "circle", "dots", "star", ...
        #     for _ in range(10):
        #         time.sleep(0.1)
                # spinner.next()
                
            
        
    # except Exception as e:
    #     LOG.error(f"Error: {e}")
        
def getFileList(connection, client_ip, client_port, AES_KEY):
    # print('send ', create_packet("", 'F', connection))
    connection.settimeout(5)
    try:
        connection.sendall(create_packet("", client_ip, client_port, 'F', connection, AES_KEY))
        # connection.send(create_packet("", 'F', connection))
        header = connection.recv(16+15)
        header = decrypt_packet(header, AES_KEY)
        protocol_name, sender_ip, sender_port, type_request, content_length = GEYS_header_parse(header)
        data = connection.recv(content_length)
        data = decrypt_packet(data, AES_KEY)
    except connection.timeout:
        return -1
        # print(protocol_name, sender_ip, sender_port, type_request, content_length, data)
    return {
        'protocol_name': protocol_name,
        'sender_ip': sender_ip,
        'sender_port': sender_port,
        'type_request': type_request,
        'content_length': content_length,
        'data': data
    }
    
    