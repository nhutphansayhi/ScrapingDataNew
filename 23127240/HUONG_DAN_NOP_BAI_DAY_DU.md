# HƯỚNG DẪN NỘP BÀI ĐẦY ĐỦ - LAB 1

## 📋 TÓM TẮT YÊU CẦU

Theo giảng viên, bạn cần nộp 3 phần riêng biệt:

1. **Mã nguồn (Source Code)** → Nộp lên **MOODLE**
2. **Chạy & Benchmark** → Chạy trên **GOOGLE COLAB (CPU-only)**
3. **Dữ liệu (Results)** → Nộp lên **GOOGLE DRIVE**

---

## 🎯 PHẦN 1: CHUẨN BỊ MÃ NGUỒN (CHO MOODLE)

### Bước 1: Tạo thư mục nộp bài

```
23127240/
├── src/                        # Mã nguồn
│   ├── main.py
│   ├── arxiv_scraper.py
│   ├── reference_scraper.py
│   ├── config.py
│   ├── utils.py
│   └── requirements.txt       # ⭐ BẮT BUỘC
├── README.md                   # ⭐ BẮT BUỘC - Hướng dẫn chạy
└── Report.docx                 # ⭐ BẮT BUỘC - Báo cáo + link video
```

### Bước 2: Tạo requirements.txt

```bash
cd /Users/nhutphan/Desktop/testLai/23127240/src
```

Tạo file `requirements.txt`:
```txt
arxiv
requests
beautifulsoup4
bibtexparser
psutil
```

### Bước 3: Viết README.md chi tiết

File `README.md` phải bao gồm:
- Python version (ví dụ: Python 3.8+)
- Cách cài đặt dependencies
- **Cách chạy trên Google Colab** (quan trọng!)
- Cấu hình paper range
- Giải thích về performance metrics

### Bước 4: Nén và nộp lên Moodle

```bash
cd /Users/nhutphan/Desktop/testLai
zip -r 23127240.zip 23127240/ -x "*/23127240_data/*" -x "*/__pycache__/*" -x "*/.DS_Store"
```

**Upload `23127240.zip` lên Moodle**

---

## 🚀 PHẦN 2: CHẠY TRÊN GOOGLE COLAB (CPU-ONLY)

### Bước 1: Đưa code lên GitHub (để dễ clone vào Colab)

```bash
# Trong thư mục dự án
cd /Users/nhutphan/Desktop/testLai/23127240

# Khởi tạo git (nếu chưa có)
git init
git add .
git commit -m "Initial commit for Lab 1"

# Push lên GitHub
git remote add origin https://github.com/nhutphansayhi/ScrapingData.git
git push -u origin master
```

### Bước 2: Mở Google Colab

1. Truy cập: https://colab.research.google.com/
2. **File > New notebook**
3. Đặt tên: `ArXiv_Scraper_23127240_Final.ipynb`
4. **Runtime > Change runtime type > Hardware accelerator > None** (CPU-only)

### Bước 3: Chạy các cell theo thứ tự

#### Cell 1: Kiểm tra Runtime
```python
import psutil
import platform

print("=" * 60)
print("RUNTIME INFO - Lab 1 Testbed")
print("=" * 60)
print(f"OS: {platform.system()} {platform.release()}")
print(f"CPU cores: {psutil.cpu_count()}")
print(f"RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
print(f"Disk: {psutil.disk_usage('/').total / (1024**3):.2f} GB")
print("=" * 60)

# Verify CPU-only
try:
    import torch
    if torch.cuda.is_available():
        print("\n⚠️  WARNING: GPU detected! Switch to CPU-only")
    else:
        print("\n✅ CPU-only mode - Correct!")
except:
    print("\n✅ CPU-only mode - Correct!")
```

#### Cell 2: Clone từ GitHub
```python
!git clone https://github.com/nhutphansayhi/ScrapingData.git
%cd ScrapingData/23127240
!ls -la src/
```

#### Cell 3: Install dependencies
```python
!pip install -q -r src/requirements.txt

import arxiv
import requests
from bs4 import BeautifulSoup
import bibtexparser
import psutil
import json
import time
from datetime import datetime

print("✅ All dependencies installed!")
```

#### Cell 4: Setup Performance Monitor
```python
import psutil
import time
import os
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.max_ram_mb = 0
        self.initial_disk_mb = 0
        
    def start(self):
        self.start_time = time.time()
        self.initial_disk_mb = psutil.disk_usage('/').used / (1024**2)
        print(f"🚀 Started at: {datetime.now()}")
        print(f"Initial RAM: {psutil.virtual_memory().used / (1024**2):.2f} MB")
        
    def update_metrics(self):
        current_ram_mb = psutil.virtual_memory().used / (1024**2)
        self.max_ram_mb = max(self.max_ram_mb, current_ram_mb)
        
    def finish(self, output_dir="23127240_data"):
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        
        final_disk_mb = psutil.disk_usage('/').used / (1024**2)
        disk_increase = final_disk_mb - self.initial_disk_mb
        
        output_size = 0
        if os.path.exists(output_dir):
            output_size = sum(
                os.path.getsize(os.path.join(dp, f))
                for dp, dn, filenames in os.walk(output_dir)
                for f in filenames
            ) / (1024**2)
        
        print("\n" + "=" * 70)
        print("📊 PERFORMANCE METRICS - LAB 1")
        print("=" * 70)
        print(f"\n⏱️  WALL TIME: {total_time:.2f}s ({total_time/60:.2f} min)")
        print(f"💾 MAX RAM: {self.max_ram_mb:.2f} MB ({self.max_ram_mb/1024:.2f} GB)")
        print(f"💿 DISK INCREASE: {disk_increase:.2f} MB")
        print(f"📦 OUTPUT SIZE: {output_size:.2f} MB")
        print("=" * 70)
        
        return {
            'testbed': 'Google Colab CPU-only',
            'wall_time_seconds': total_time,
            'wall_time_minutes': total_time / 60,
            'max_ram_mb': self.max_ram_mb,
            'disk_increase_mb': disk_increase,
            'output_size_mb': output_size,
            'timestamp': datetime.now().isoformat()
        }

monitor = PerformanceMonitor()
print("✅ Monitor ready!")
```

#### Cell 5: Chạy Scraper (END-TO-END)
```python
# START MONITORING
monitor.start()

# Di chuyển vào src
%cd /content/ScrapingData/23127240/src

# Kiểm tra file có sẵn
print("📂 Available Python files:")
!ls -la *.py

# Chạy scraper (thay main.py bằng tên file đúng nếu cần)
print("\n🚀 Running scraper...")
!python3 main.py

# Cập nhật metrics
monitor.update_metrics()

# Về thư mục gốc
%cd /content/ScrapingData/23127240

# FINISH MONITORING
metrics = monitor.finish()

# Lưu metrics
with open('performance_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("\n✅ Scraping completed!")
print("💾 Metrics saved to performance_metrics.json")
```

#### Cell 6: Verify Data Structure
```python
import os
import json

data_dir = "23127240_data"

if os.path.exists(data_dir):
    papers = [d for d in os.listdir(data_dir) 
              if os.path.isdir(os.path.join(data_dir, d))]
    
    print(f"📊 Total papers: {len(papers)}")
    
    # Check first paper
    if papers:
        paper = papers[0]
        paper_path = os.path.join(data_dir, paper)
        
        print(f"\n📄 Sample paper: {paper}")
        print(f"  - tex/ exists: {os.path.exists(os.path.join(paper_path, 'tex'))}")
        print(f"  - metadata.json exists: {os.path.exists(os.path.join(paper_path, 'metadata.json'))}")
        print(f"  - references.json exists: {os.path.exists(os.path.join(paper_path, 'references.json'))}")
else:
    print("❌ Data directory not found!")
```

---

## 💾 PHẦN 3: NỘP DỮ LIỆU LÊN GOOGLE DRIVE

### Bước 1: Nén dữ liệu trong Colab

#### Cell 7: Zip data
```python
import shutil

# Nén dữ liệu
print("📦 Compressing data...")
shutil.make_archive('23127240_data', 'zip', '.', '23127240_data')

size_mb = os.path.getsize('23127240_data.zip') / (1024**2)
print(f"✅ Created: 23127240_data.zip")
print(f"📊 Size: {size_mb:.2f} MB ({size_mb/1024:.2f} GB)")
```

### Bước 2: Upload lên Google Drive

#### Cell 8: Mount Drive và Copy
```python
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Copy file lên Drive
!cp 23127240_data.zip /content/drive/MyDrive/
!cp performance_metrics.json /content/drive/MyDrive/

print("✅ Files uploaded to Google Drive:")
print("   - 23127240_data.zip")
print("   - performance_metrics.json")
```

### Bước 3: Upload vào thư mục giảng viên chỉ định

1. Mở Google Drive trên trình duyệt
2. Tìm file `23127240_data.zip` trong **My Drive**
3. **Di chuyển hoặc copy** file này vào **thư mục Google Drive do giảng viên cung cấp**
4. Đảm bảo file có tên đúng: `23127240.zip` (theo Student ID)

---

## 📝 PHẦN 4: HOÀN THIỆN BÁO CÁO

### Trong Report.docx, bạn cần ghi:

#### 1. Testbed
```
Testbed: Google Colab instance, CPU-only mode
OS: Linux (từ Cell 1)
CPU: X cores (từ Cell 1)
RAM: Y GB (từ Cell 1)
```

#### 2. Running Time (Wall Time)
```
Total wall time: X seconds (Y minutes)
Average per paper: Z seconds
Papers processed: N papers
```

#### 3. Memory Footprint
```
Maximum RAM used: X MB (Y GB)
Disk increase: Z MB
Output data size: W MB
```

#### 4. Data Statistics
```
Total papers scraped: N
Papers with TeX sources: X
Papers with metadata: Y
Papers with references: Z
Success rate: XX%
```

#### 5. Link YouTube Video
```
Video demo: https://youtube.com/watch?v=xxxxx
(Video ≤120 giây, công khai, giữ ít nhất 1 tháng sau khi có điểm)
```

---

## 🎬 PHẦN 5: QUAY VIDEO DEMO (≤120 GIÂY)

### Script video (120s):

**[0-15s] Setup**
- "Xin chào, tôi là sinh viên MSSV 23127240"
- "Đây là demo Lab 1 chạy trên Google Colab CPU-only"
- Show Runtime settings (CPU-only)

**[15-30s] Clone & Setup**
- Clone repository từ GitHub
- Install dependencies
- Show code structure

**[30-75s] Running**
- Chạy scraper
- Show logs: downloading, extracting, removing figures
- Show performance metrics trong quá trình chạy

**[75-105s] Results**
- Show performance metrics cuối cùng
- Verify data structure
- Show một paper mẫu (tex/, metadata.json, references.json)

**[105-120s] Summary**
- Tóm tắt: "Scraper đã chạy thành công trên Colab CPU-only"
- "Đo được wall time X phút, max RAM Y GB"
- "Dữ liệu đã được nộp lên Google Drive"

---

## ✅ CHECKLIST TRƯỚC KHI NỘP

### Moodle (Source Code):
- [ ] File 23127240.zip chứa src/, README.md, Report.docx
- [ ] requirements.txt đầy đủ
- [ ] README.md có hướng dẫn chạy trên Colab
- [ ] Report.docx có link video YouTube

### Google Drive (Data):
- [ ] File 23127240_data.zip (hoặc 23127240.zip)
- [ ] Upload vào đúng thư mục giảng viên chỉ định
- [ ] File không corrupt, có thể extract được

### YouTube (Video):
- [ ] Video ≤120 giây
- [ ] Công khai (Public)
- [ ] Link đã copy vào Report.docx
- [ ] Đã test link hoạt động

### Colab (Benchmark):
- [ ] Đã chạy trên CPU-only mode
- [ ] Có performance metrics
- [ ] Kết quả đã verify

---

## 🎯 LUỒNG CÔNG VIỆC TỔNG THỂ

```
1. Viết code local
   ↓
2. Test local
   ↓
3. Push code lên GitHub
   ↓
4. Nén code → Nộp MOODLE (23127240.zip)
   ↓
5. Mở Google Colab (CPU-only)
   ↓
6. Clone từ GitHub vào Colab
   ↓
7. Chạy scraper + đo metrics
   ↓
8. Nén dữ liệu → Upload Google Drive
   ↓
9. Copy file vào thư mục giảng viên
   ↓
10. Ghi metrics vào Report.docx
   ↓
11. Quay video demo
   ↓
12. Upload YouTube + copy link vào Report
   ↓
13. Update Report.docx trong file nộp Moodle
   ↓
14. HOÀN TẤT! ✅
```

---

## 📞 LƯU Ý QUAN TRỌNG

1. **Code trên GitHub**: Chỉ để tiện clone vào Colab, KHÔNG phải nơi nộp chính thức
2. **Testbed bắt buộc**: Google Colab CPU-only (không được dùng GPU hay máy local)
3. **3 nơi nộp khác nhau**:
   - Moodle: Source code + Report + README
   - Google Drive: Dữ liệu đã scrape
   - YouTube: Video demo
4. **Không được nộp muộn**: Đảm bảo nộp đúng deadline

---

**Chúc bạn hoàn thành xuất sắc Lab 1! 🚀**
