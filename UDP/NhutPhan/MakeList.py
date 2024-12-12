import os

def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    if size_mb >= 1024:
        size_gb = size_mb / 1024
        return f"{size_gb:.2f}GB"
    else:
        return f"{size_mb:.2f}MB"

def create_file_list(directory, output_file):
    with open(output_file, 'w') as f:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                size = get_file_size(file_path)
                f.write(f"{filename} {size}\n")

if __name__ == "__main__":
    create_file_list("database", "files.txt")