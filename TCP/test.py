import threading
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
import time

# Giả lập hàm tải chunk
def download_chunk(file_name, offset, length, thread_id, progress, task_id):
    chunk_downloaded = 0
    while chunk_downloaded < length:
        time.sleep(0.1)  # Giả lập tải dữ liệu
        chunk_size = min(1024, length - chunk_downloaded)  # Tải 1024 byte mỗi lần
        chunk_downloaded += chunk_size
        progress.update(task_id, advance=chunk_size)

# Main function
def main():
    CHUNK_NUMBER = 4
    file_size = 100000  # Giả lập tệp có kích thước 100,000 byte
    file_name = "example_file"
    
    chunk_size = (file_size + CHUNK_NUMBER - 1) // CHUNK_NUMBER
    threads = []
    
    # Khởi tạo thanh tiến trình
    progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    )
    
    with progress:
        # Tạo task cho từng luồng
        task_ids = []
        for i in range(CHUNK_NUMBER):
            offset = chunk_size * i
            length = min(chunk_size, file_size - offset)
            task_id = progress.add_task(f"Chunk {i+1}", total=length)
            task_ids.append(task_id)
            
            # Tạo thread
            thr = threading.Thread(
                target=download_chunk,
                args=(file_name, offset, length, i+1, progress, task_id)
            )
            thr.start()
            threads.append(thr)
        
        # Đợi tất cả các thread hoàn thành
        for thr in threads:
            thr.join()

if __name__ == "__main__":
    main()
