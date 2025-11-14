# HƯỚNG DẪN CHẠY SCRAPER TRÊN GOOGLE COLAB

## 📋 TỔNG QUAN

Hướng dẫn này giúp bạn chạy arXiv scraper trên Google Colab để thu thập dữ liệu các bài báo còn lại theo yêu cầu Lab 1.

**Yêu cầu từ Lab 1:**
- Testbed: Google Colab instance, CPU-only mode
- Đo wall time (thời gian chạy end-to-end)
- Đo memory footprint (RAM tối đa, disk usage)
- Thu thập: TeX sources, metadata.json, references.json
- Loại bỏ tất cả hình ảnh (figures) để giảm kích thước

---

## 🚀 BƯỚC 1: MỞ GOOGLE COLAB

1. Truy cập: https://colab.research.google.com/
2. Đăng nhập Google Account
3. Tạo notebook mới: **File > New notebook**
4. Đổi tên notebook: `ArXiv_Scraper_23127240.ipynb`

---

## ⚙️ BƯỚC 2: SETUP MÔI TRƯỜNG

### Cell 1: Kiểm tra Runtime (CPU-only)

```python
# Kiểm tra runtime type (phải là CPU theo yêu cầu Lab 1)
import psutil
import platform

print("=" * 60)
print("THÔNG TIN RUNTIME")
print("=" * 60)
print(f"OS: {platform.system()} {platform.release()}")
print(f"CPU cores: {psutil.cpu_count()}")
print(f"RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
print(f"Disk: {psutil.disk_usage('/').total / (1024**3):.2f} GB")
print("=" * 60)

# Đảm bảo không có GPU (theo yêu cầu CPU-only)
try:
    import torch
    if torch.cuda.is_available():
        print("⚠️ WARNING: GPU detected! Lab yêu cầu CPU-only mode")
        print("Chuyển sang Runtime > Change runtime type > Hardware accelerator > None")
    else:
        print("✅ CPU-only mode - Đúng yêu cầu Lab 1")
except:
    print("✅ CPU-only mode - Đúng yêu cầu Lab 1")
```

**Action**: Chạy cell này, nếu thấy GPU warning thì đổi sang CPU:
- Runtime > Change runtime type > Hardware accelerator > **None**

---

### Cell 2: Clone Repository

```python
# Clone source code từ GitHub
!git clone https://github.com/nhutphansayhi/ScrapingData.git
%cd ScrapingData/23127371
!ls -la
```

---

### Cell 3: Cài đặt Dependencies

```python
# Cài đặt thư viện cần thiết
!pip install -q arxiv requests beautifulsoup4 bibtexparser psutil

# Verify installation
import arxiv
import requests
from bs4 import BeautifulSoup
import bibtexparser
import psutil
import json
import time

print("✅ Tất cả thư viện đã được cài đặt!")
```

---

## 📊 BƯỚC 3: TẠO MONITORING SCRIPT

### Cell 4: Setup Memory & Time Tracking

```python
import psutil
import time
import os
from datetime import datetime

class PerformanceMonitor:
    """Theo dõi performance theo yêu cầu Lab 1"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.max_ram_mb = 0
        self.max_disk_mb = 0
        self.paper_times = []
        
    def start(self):
        """Bắt đầu đo wall time"""
        self.start_time = time.time()
        print(f"🚀 Bắt đầu scraping: {datetime.now()}")
        
    def update(self, paper_id, paper_time):
        """Cập nhật metrics cho mỗi paper"""
        # RAM usage
        ram_mb = psutil.virtual_memory().used / (1024**2)
        self.max_ram_mb = max(self.max_ram_mb, ram_mb)
        
        # Disk usage
        disk_mb = psutil.disk_usage('/').used / (1024**2)
        self.max_disk_mb = max(self.max_disk_mb, disk_mb)
        
        # Paper processing time
        self.paper_times.append({
            'paper_id': paper_id,
            'time_seconds': paper_time
        })
        
    def finish(self):
        """Kết thúc và tính toán metrics"""
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        
        print("\n" + "=" * 70)
        print("📊 PERFORMANCE METRICS (theo yêu cầu Lab 1)")
        print("=" * 70)
        
        # Wall time
        print(f"\n⏱️  WALL TIME (End-to-End):")
        print(f"   Total: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        
        if self.paper_times:
            avg_time = sum(p['time_seconds'] for p in self.paper_times) / len(self.paper_times)
            print(f"   Average per paper: {avg_time:.2f} seconds")
            print(f"   Papers processed: {len(self.paper_times)}")
        
        # Memory footprint
        print(f"\n💾 MEMORY FOOTPRINT:")
        print(f"   Maximum RAM used: {self.max_ram_mb:.2f} MB ({self.max_ram_mb/1024:.2f} GB)")
        current_ram = psutil.virtual_memory().used / (1024**2)
        print(f"   Current RAM: {current_ram:.2f} MB")
        
        # Disk usage
        print(f"\n💿 DISK USAGE:")
        print(f"   Maximum disk used: {self.max_disk_mb:.2f} MB ({self.max_disk_mb/1024:.2f} GB)")
        
        # Calculate output size
        output_dir = "23127240_data"
        if os.path.exists(output_dir):
            total_size = sum(
                os.path.getsize(os.path.join(dp, f))
                for dp, dn, filenames in os.walk(output_dir)
                for f in filenames
            )
            print(f"   Output data size: {total_size/(1024**2):.2f} MB ({total_size/(1024**3):.2f} GB)")
        
        print("=" * 70)
        
        return {
            'total_wall_time_seconds': total_time,
            'max_ram_mb': self.max_ram_mb,
            'max_disk_mb': self.max_disk_mb,
            'papers_processed': len(self.paper_times),
            'avg_time_per_paper': avg_time if self.paper_times else 0,
            'paper_times': self.paper_times
        }

# Khởi tạo monitor
monitor = PerformanceMonitor()
print("✅ Performance Monitor đã sẵn sàng!")
```

---

## 🔧 BƯỚC 4: CHẠY SCRAPER

### Cell 5: Chạy Main Script với Monitoring

```python
import sys
import os

# Thêm src vào Python path
sys.path.insert(0, '/content/ScrapingData/23127371/src')

# Import scraper modules
from main import main as run_scraper
from config import *

# BẮT ĐẦU ĐO WALL TIME
monitor.start()

try:
    # Chạy scraper (end-to-end)
    # Script sẽ tự động:
    # - Scrape metadata
    # - Download TeX sources
    # - Remove figures (theo yêu cầu Lab 1)
    # - Crawl references từ Semantic Scholar
    # - Lưu vào 23127240_data/
    
    print("🔄 Đang chạy scraper...")
    print("   - Entry discovery: arXiv API")
    print("   - Source download: .tar.gz extraction")
    print("   - Figure removal: Tự động xóa ảnh")
    print("   - Reference crawling: Semantic Scholar API")
    print("\n")
    
    run_scraper()
    
except Exception as e:
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()
finally:
    # KẾT THÚC ĐO WALL TIME
    metrics = monitor.finish()
    
    # Lưu metrics để báo cáo
    with open('performance_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("\n✅ Metrics đã được lưu vào performance_metrics.json")
```

**Lưu ý**: Script sẽ chạy trong vài phút đến vài giờ tùy số lượng papers. Monitor sẽ tự động đo wall time và memory.

---

## 📁 BƯỚC 5: KIỂM TRA OUTPUT

### Cell 6: Verify Data Structure

```python
import os
import json

def verify_data_structure(data_dir="23127240_data"):
    """Kiểm tra cấu trúc dữ liệu theo yêu cầu Lab 1"""
    
    print("=" * 70)
    print("📁 KIỂM TRA CẤU TRÚC DỮ LIỆU")
    print("=" * 70)
    
    if not os.path.exists(data_dir):
        print(f"❌ Thư mục {data_dir} không tồn tại!")
        return
    
    papers = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    print(f"\n📊 Tổng số papers: {len(papers)}")
    
    stats = {
        'total_papers': len(papers),
        'papers_with_tex': 0,
        'papers_with_metadata': 0,
        'papers_with_references': 0,
        'total_versions': 0,
        'total_tex_files': 0,
        'total_bib_files': 0,
        'papers_missing_figures': 0
    }
    
    for paper_id in papers[:5]:  # Check first 5 papers
        paper_path = os.path.join(data_dir, paper_id)
        print(f"\n📄 {paper_id}:")
        
        # Check tex folder
        tex_path = os.path.join(paper_path, "tex")
        if os.path.exists(tex_path):
            versions = os.listdir(tex_path)
            stats['papers_with_tex'] += 1
            stats['total_versions'] += len(versions)
            print(f"   ✅ tex/ - {len(versions)} version(s)")
            
            # Count .tex and .bib files
            for version in versions:
                version_path = os.path.join(tex_path, version)
                for root, dirs, files in os.walk(version_path):
                    stats['total_tex_files'] += len([f for f in files if f.endswith('.tex')])
                    stats['total_bib_files'] += len([f for f in files if f.endswith('.bib')])
        else:
            print(f"   ❌ tex/ missing")
        
        # Check metadata.json
        metadata_path = os.path.join(paper_path, "metadata.json")
        if os.path.exists(metadata_path):
            stats['papers_with_metadata'] += 1
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                print(f"   ✅ metadata.json - Title: {metadata.get('title', 'N/A')[:50]}...")
        else:
            print(f"   ❌ metadata.json missing")
        
        # Check references.json
        ref_path = os.path.join(paper_path, "references.json")
        if os.path.exists(ref_path):
            stats['papers_with_references'] += 1
            with open(ref_path, 'r') as f:
                refs = json.load(f)
                print(f"   ✅ references.json - {len(refs)} reference(s) with arXiv IDs")
        else:
            print(f"   ❌ references.json missing")
    
    print("\n" + "=" * 70)
    print("📊 STATISTICS SUMMARY")
    print("=" * 70)
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print("=" * 70)
    
    return stats

# Chạy verification
stats = verify_data_structure()
```

---

## 📥 BƯỚC 6: DOWNLOAD DỮ LIỆU

### Cell 7: Nén và Download

```python
import shutil
from google.colab import files

# Nén dữ liệu
print("📦 Đang nén dữ liệu...")
shutil.make_archive('23127240_data', 'zip', '.', '23127240_data')
print(f"✅ Đã tạo 23127240_data.zip")

# Kiểm tra kích thước
size_mb = os.path.getsize('23127240_data.zip') / (1024**2)
print(f"📊 Kích thước: {size_mb:.2f} MB")

if size_mb > 100:
    print("⚠️ File lớn hơn 100MB, có thể download chậm")
    print("💡 Khuyến nghị: Upload lên Google Drive thay vì download trực tiếp")
else:
    print("\n⬇️ Bắt đầu download...")
    files.download('23127240_data.zip')
```

**Nếu file quá lớn, upload lên Google Drive:**

```python
# Cell 8: Upload to Google Drive (nếu file quá lớn)
from google.colab import drive
drive.mount('/content/drive')

# Copy vào Drive
!cp 23127240_data.zip /content/drive/MyDrive/
print("✅ Đã upload vào Google Drive > MyDrive > 23127240_data.zip")
```

---

## 📊 BƯỚC 7: XEM PERFORMANCE REPORT

### Cell 9: Load và Hiển thị Metrics

```python
# Load performance metrics
with open('performance_metrics.json', 'r') as f:
    metrics = json.load(f)

print("=" * 70)
print("📈 FINAL PERFORMANCE REPORT (cho Report.docx)")
print("=" * 70)

print("\n🎯 YÊU CẦU LAB 1 - TESTBED: Google Colab CPU-only")
print("-" * 70)

print("\n⏱️  RUNNING TIME:")
print(f"   • Total wall time: {metrics['total_wall_time_seconds']:.2f}s ({metrics['total_wall_time_seconds']/60:.2f} min)")
print(f"   • Average time per paper: {metrics['avg_time_per_paper']:.2f}s")
print(f"   • Papers processed: {metrics['papers_processed']}")

print("\n💾 MEMORY FOOTPRINT:")
print(f"   • Maximum RAM used: {metrics['max_ram_mb']:.2f} MB ({metrics['max_ram_mb']/1024:.2f} GB)")
print(f"   • Maximum disk used: {metrics['max_disk_mb']:.2f} MB ({metrics['max_disk_mb']/1024:.2f} GB)")

print("\n📊 DATA STATISTICS:")
if stats:
    print(f"   • Total papers: {stats['total_papers']}")
    print(f"   • Papers with TeX: {stats['papers_with_tex']}")
    print(f"   • Total versions: {stats['total_versions']}")
    print(f"   • Total .tex files: {stats['total_tex_files']}")
    print(f"   • Total .bib files: {stats['total_bib_files']}")

print("\n✅ Copy metrics này vào Report.docx!")
print("=" * 70)
```

---

## 🎬 BƯỚC 8: GHI CHÚ CHO DEMO VIDEO

Khi quay video demo (≤120s), hãy bao gồm:

1. **Setup (15s)**:
   - Mở Colab
   - Show Runtime = CPU-only
   - Clone repo

2. **Running (45s)**:
   - Chạy scraper
   - Show logs: downloading, extracting, removing figures
   - Show memory tracking

3. **Results (45s)**:
   - Show performance metrics
   - Verify data structure
   - Show một paper mẫu (tex/, metadata.json, references.json)

4. **Voice explanation**:
   - "Scraper chạy trên Colab CPU-only theo yêu cầu Lab 1"
   - "Tự động đo wall time và memory footprint"
   - "Remove figures để giảm kích thước"
   - "Crawl references từ Semantic Scholar"

---

## ⚠️ LƯU Ý QUAN TRỌNG

### Rate Limiting (Semantic Scholar)
- **1 request/second**, 100 requests/5 minutes
- Script có built-in retry mechanism
- Nếu gặp 429 error, đợi 5 phút rồi chạy lại

### Colab Timeout
- Free tier: 12h max runtime
- Nếu scraping quá nhiều papers, chia nhỏ range

### Disk Space
- Colab free: ~100GB disk
- Monitor disk usage trong Cell 6
- Nếu full, download từng batch

### Figures Removal
- Script tự động xóa: .png, .jpg, .jpeg, .pdf, .eps
- Giảm ~70-80% kích thước theo kinh nghiệm

---

## 🆘 TROUBLESHOOTING

**Lỗi "No module named 'arxiv'":**
```python
!pip install --upgrade arxiv
```

**Lỗi "Rate limit exceeded":**
```python
# Đợi 5 phút rồi chạy lại
import time
time.sleep(300)
```

**Lỗi "Disk full":**
```python
# Xóa cache
!rm -rf ~/.cache/
!rm -rf /tmp/*
```

**Script chạy quá lâu:**
- Giảm MAX_PAPERS trong config.py
- Hoặc chia nhỏ paper range

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Kiểm tra logs trong Cell 5
2. Xem performance_metrics.json
3. Liên hệ: hlhdang@fit.hcmus.edu.vn

---

**Chúc bạn scraping thành công! 🚀**
