# HƯỚNG DẪN CHẠY SCRAPER TRÊN GOOGLE COLAB TỪ ĐẦU

## 📋 YÊU CẦU LAB 1

Theo đề bài, bạn cần:
- **Testbed**: Google Colab CPU-only mode
- **Đo lường**: Wall time (end-to-end), Memory footprint (max RAM, disk usage)
- **Thu thập**: TeX sources, metadata.json, references.json
- **Tối ưu**: Xóa figures để giảm kích thước

---

## 🚀 BƯỚC 1: MỞ GOOGLE COLAB

1. Truy cập: https://colab.research.google.com/
2. Đăng nhập Google Account
3. **File > New notebook**
4. Đổi tên: `ArXiv_Scraper_23127240.ipynb`

---

## ⚙️ BƯỚC 2: SETUP RUNTIME (QUAN TRỌNG!)

### Chuyển sang CPU-only mode:
1. **Runtime > Change runtime type**
2. **Hardware accelerator > None** (CPU-only theo yêu cầu Lab)
3. Click **Save**

### Cell 1: Kiểm tra Runtime

```python
import psutil
import platform

print("=" * 60)
print("THÔNG TIN RUNTIME - Lab 1 Requirements")
print("=" * 60)
print(f"OS: {platform.system()} {platform.release()}")
print(f"CPU cores: {psutil.cpu_count()}")
print(f"Total RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
print(f"Total Disk: {psutil.disk_usage('/').total / (1024**3):.2f} GB")
print("=" * 60)

# Kiểm tra CPU-only (không có GPU)
try:
    import torch
    if torch.cuda.is_available():
        print("\n⚠️  WARNING: GPU detected!")
        print("👉 Lab yêu cầu CPU-only mode")
        print("   Runtime > Change runtime type > Hardware accelerator > None")
    else:
        print("\n✅ CPU-only mode - Đúng yêu cầu Lab 1")
except:
    print("\n✅ CPU-only mode - Đúng yêu cầu Lab 1")
```

**Chạy cell này và đảm bảo thấy "✅ CPU-only mode"**

---

## 📥 BƯỚC 3: CLONE REPOSITORY

### Cell 2: Clone source code

```python
# Clone repository từ GitHub
!git clone https://github.com/nhutphansayhi/ScrapingData.git

# Di chuyển vào thư mục project
%cd ScrapingData/23127240

# Kiểm tra cấu trúc
print("\n📁 Project Structure:")
!ls -la

print("\n📂 Source Code:")
!ls -la src/
```

---

## 🔧 BƯỚC 4: CÀI ĐẶT DEPENDENCIES

### Cell 3: Install requirements

```python
# Cài đặt các thư viện cần thiết
!pip install -q -r src/requirements.txt

# Verify installation
import arxiv
import requests
from bs4 import BeautifulSoup
import bibtexparser
import psutil
import json
import time
from datetime import datetime

print("✅ Tất cả thư viện đã được cài đặt thành công!")
print("\nCác thư viện chính:")
print("  - arxiv: Entry discovery")
print("  - requests: HTTP requests")
print("  - beautifulsoup4: HTML parsing")
print("  - bibtexparser: BibTeX parsing")
print("  - psutil: Performance monitoring")
```

---

## 📊 BƯỚC 5: SETUP PERFORMANCE MONITOR

### Cell 4: Tạo Performance Monitor (theo yêu cầu Lab 1)

```python
import psutil
import time
import os
from datetime import datetime

class PerformanceMonitor:
    """
    Monitor để đo wall time và memory footprint theo yêu cầu Lab 1
    """
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.max_ram_mb = 0
        self.initial_disk_mb = 0
        self.paper_count = 0
        self.paper_times = []
        
    def start(self):
        """Bắt đầu đo wall time (end-to-end)"""
        self.start_time = time.time()
        self.initial_disk_mb = psutil.disk_usage('/').used / (1024**2)
        
        print("=" * 70)
        print("🚀 BẮT ĐẦU SCRAPING - LAB 1 PERFORMANCE MONITORING")
        print("=" * 70)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Initial RAM: {psutil.virtual_memory().used / (1024**2):.2f} MB")
        print(f"Initial Disk: {self.initial_disk_mb:.2f} MB")
        print("=" * 70)
        
    def update_metrics(self):
        """Cập nhật metrics trong quá trình scraping"""
        # Đo RAM usage
        current_ram_mb = psutil.virtual_memory().used / (1024**2)
        self.max_ram_mb = max(self.max_ram_mb, current_ram_mb)
        
    def finish(self, output_dir="23127240_data"):
        """Kết thúc và hiển thị metrics"""
        self.end_time = time.time()
        total_time_sec = self.end_time - self.start_time
        
        # Tính disk increase
        final_disk_mb = psutil.disk_usage('/').used / (1024**2)
        disk_increase_mb = final_disk_mb - self.initial_disk_mb
        
        # Tính output size
        output_size_mb = 0
        if os.path.exists(output_dir):
            total_bytes = sum(
                os.path.getsize(os.path.join(dp, f))
                for dp, dn, filenames in os.walk(output_dir)
                for f in filenames
            )
            output_size_mb = total_bytes / (1024**2)
        
        # Hiển thị report
        print("\n" + "=" * 70)
        print("📊 PERFORMANCE METRICS - LAB 1 REQUIREMENTS")
        print("=" * 70)
        
        print("\n🎯 TESTBED: Google Colab CPU-only mode")
        print("-" * 70)
        
        # 1. RUNNING TIME (Wall Time - End-to-End)
        print("\n⏱️  RUNNING TIME:")
        print(f"   • Total wall time: {total_time_sec:.2f} seconds")
        print(f"   • In minutes: {total_time_sec/60:.2f} minutes")
        print(f"   • In hours: {total_time_sec/3600:.2f} hours")
        
        if self.paper_times:
            avg_time = sum(self.paper_times) / len(self.paper_times)
            print(f"   • Papers processed: {len(self.paper_times)}")
            print(f"   • Average per paper: {avg_time:.2f} seconds")
        
        # 2. MEMORY FOOTPRINT
        print("\n💾 MEMORY FOOTPRINT:")
        print(f"   • Maximum RAM used: {self.max_ram_mb:.2f} MB ({self.max_ram_mb/1024:.2f} GB)")
        print(f"   • Current RAM: {psutil.virtual_memory().used/(1024**2):.2f} MB")
        print(f"   • Disk increase: {disk_increase_mb:.2f} MB ({disk_increase_mb/1024:.2f} GB)")
        print(f"   • Output data size: {output_size_mb:.2f} MB ({output_size_mb/1024:.2f} GB)")
        
        print("\n" + "=" * 70)
        print("✅ Copy metrics này vào Report.docx!")
        print("=" * 70)
        
        # Lưu metrics
        metrics = {
            'testbed': 'Google Colab CPU-only',
            'total_wall_time_seconds': total_time_sec,
            'total_wall_time_minutes': total_time_sec / 60,
            'total_wall_time_hours': total_time_sec / 3600,
            'max_ram_mb': self.max_ram_mb,
            'max_ram_gb': self.max_ram_mb / 1024,
            'disk_increase_mb': disk_increase_mb,
            'disk_increase_gb': disk_increase_mb / 1024,
            'output_size_mb': output_size_mb,
            'output_size_gb': output_size_mb / 1024,
            'papers_processed': len(self.paper_times),
            'avg_time_per_paper': sum(self.paper_times)/len(self.paper_times) if self.paper_times else 0,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(self.end_time).isoformat()
        }
        
        return metrics

# Khởi tạo monitor
monitor = PerformanceMonitor()
print("✅ Performance Monitor đã sẵn sàng theo yêu cầu Lab 1!")
```

---

## 🔄 BƯỚC 6: CHẠY SCRAPER (END-TO-END)

### Cell 5A: Kiểm tra files trong src/

```python
# Di chuyển vào thư mục src
%cd /content/ScrapingData/23127240/src

# Kiểm tra files Python
print("📂 Python files trong src/:")
!ls -la *.py

# Kiểm tra nội dung thư mục
print("\n� All files:")
!ls -la
```

### Cell 5B: Chạy scraper trực tiếp (RECOMMENDED)

**Cách này KHÔNG CẦN import module, chạy trực tiếp qua terminal**

```python
import subprocess
import sys
import os

# Di chuyển vào thư mục project root
%cd /content/ScrapingData/23127240

# BẮT ĐẦU ĐO WALL TIME (End-to-End)
monitor.start()

try:
    print("\n🔄 Đang chạy scraper...")
    print("\nQuy trình (theo đề bài Lab 1):")
    print("  1️⃣  Entry Discovery: arXiv API")
    print("  2️⃣  Source Download: .tar.gz extraction")
    print("  3️⃣  Figure Removal: Xóa png, jpg, pdf, eps")
    print("  4️⃣  Reference Crawling: Semantic Scholar API")
    print("  5️⃣  Data Organization: tex/, metadata.json, references.json")
    print("\n" + "-" * 70)
    
    # Chạy scraper bằng subprocess (chạy như terminal command)
    # Tìm file Python chính trong src/
    src_dir = "src"
    python_files = [f for f in os.listdir(src_dir) if f.endswith('.py')]
    
    print(f"\n📄 Python files found: {python_files}")
    
    # Thử các tên file phổ biến
    main_file = None
    for filename in ['main.py', 'scraper.py', 'arxiv_scraper.py', 'run.py']:
        if filename in python_files:
            main_file = filename
            break
    
    if main_file:
        print(f"\n🚀 Chạy: {main_file}")
        
        # Chạy script
        result = subprocess.run(
            [sys.executable, os.path.join(src_dir, main_file)],
            capture_output=True,
            text=True,
            cwd='/content/ScrapingData/23127240'
        )
        
        # Hiển thị output
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("\n✅ Scraping hoàn tất!")
        else:
            print(f"\n⚠️  Script exited with code: {result.returncode}")
    else:
        print("\n❌ Không tìm thấy file main script!")
        print("📝 Danh sách files:")
        for f in python_files:
            print(f"  - {f}")
        raise FileNotFoundError("Main script not found")
    
    # Cập nhật metrics
    monitor.update_metrics()
    
except KeyboardInterrupt:
    print("\n⚠️  Scraping bị ngắt bởi user")
except Exception as e:
    print(f"\n❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()
finally:
    # KẾT THÚC ĐO WALL TIME
    metrics = monitor.finish()
    
    # Lưu metrics
    with open('performance_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("\n💾 Metrics đã lưu vào: performance_metrics.json")
```

### Cell 5C: HOẶC chạy trực tiếp bằng ! (đơn giản nhất)

```python
# BẮT ĐẦU ĐO WALL TIME
monitor.start()

# Di chuyển vào src và chạy
%cd /content/ScrapingData/23127240/src

# Chạy trực tiếp (thay main.py bằng tên file thực tế nếu khác)
!python3 main.py

# Về thư mục gốc
%cd /content/ScrapingData/23127240

# KẾT THÚC ĐO WALL TIME
metrics = monitor.finish()

# Lưu metrics
with open('performance_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("\n💾 Metrics đã lưu vào: performance_metrics.json")
```

**Lưu ý**: 
- Chạy Cell 5A trước để xem tên file chính xác
- Nếu file không phải `main.py`, thay đổi tên trong Cell 5C
- Script sẽ chạy từ vài phút đến vài giờ tùy số lượng papers
- Monitor tự động đo wall time và memory footprint
- Nếu gặp lỗi 429 (rate limit), script sẽ tự động retry

---

## 📁 BƯỚC 7: KIỂM TRA OUTPUT

### Cell 6: Verify data structure

```python
import os
import json

def verify_data_structure(data_dir="23127240_data"):
    """Kiểm tra cấu trúc dữ liệu theo yêu cầu Lab 1"""
    
    print("=" * 70)
    print("📁 KIỂM TRA CẤU TRÚC DỮ LIỆU (theo đề bài)")
    print("=" * 70)
    
    if not os.path.exists(data_dir):
        print(f"❌ Thư mục {data_dir} không tồn tại!")
        return None
    
    # List papers
    papers = [d for d in os.listdir(data_dir) 
              if os.path.isdir(os.path.join(data_dir, d)) and d.startswith('23')]
    papers = sorted(papers)
    
    print(f"\n📊 Tổng số papers: {len(papers)}")
    
    stats = {
        'total_papers': len(papers),
        'papers_with_tex': 0,
        'papers_with_metadata': 0,
        'papers_with_references': 0,
        'total_versions': 0,
        'total_tex_files': 0,
        'total_bib_files': 0
    }
    
    # Check first 5 papers in detail
    print("\n📄 Chi tiết 5 papers đầu tiên:")
    for paper_id in papers[:5]:
        paper_path = os.path.join(data_dir, paper_id)
        print(f"\n  {paper_id}:")
        
        # Check tex/ folder
        tex_path = os.path.join(paper_path, "tex")
        if os.path.exists(tex_path):
            versions = [v for v in os.listdir(tex_path) 
                       if os.path.isdir(os.path.join(tex_path, v))]
            if versions:
                stats['papers_with_tex'] += 1
                stats['total_versions'] += len(versions)
                print(f"    ✅ tex/ - {len(versions)} version(s)")
                
                # Count .tex and .bib files
                for version in versions:
                    version_path = os.path.join(tex_path, version)
                    for root, dirs, files in os.walk(version_path):
                        tex_files = [f for f in files if f.endswith('.tex')]
                        bib_files = [f for f in files if f.endswith('.bib')]
                        stats['total_tex_files'] += len(tex_files)
                        stats['total_bib_files'] += len(bib_files)
            else:
                print(f"    ⚠️  tex/ empty (no extractable TeX)")
        else:
            print(f"    ❌ tex/ missing")
        
        # Check metadata.json
        metadata_path = os.path.join(paper_path, "metadata.json")
        if os.path.exists(metadata_path):
            stats['papers_with_metadata'] += 1
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                title = metadata.get('title', 'N/A')
                print(f"    ✅ metadata.json")
                print(f"       Title: {title[:50]}...")
        else:
            print(f"    ❌ metadata.json missing")
        
        # Check references.json
        ref_path = os.path.join(paper_path, "references.json")
        if os.path.exists(ref_path):
            stats['papers_with_references'] += 1
            with open(ref_path, 'r', encoding='utf-8') as f:
                refs = json.load(f)
                print(f"    ✅ references.json - {len(refs)} refs with arXiv IDs")
        else:
            print(f"    ⚠️  references.json missing (paper có thể không có refs)")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 STATISTICS SUMMARY")
    print("=" * 70)
    print(f"  Total papers: {stats['total_papers']}")
    print(f"  Papers with TeX: {stats['papers_with_tex']}")
    print(f"  Papers with metadata: {stats['papers_with_metadata']}")
    print(f"  Papers with references: {stats['papers_with_references']}")
    print(f"  Total versions: {stats['total_versions']}")
    print(f"  Total .tex files: {stats['total_tex_files']}")
    print(f"  Total .bib files: {stats['total_bib_files']}")
    print("=" * 70)
    
    return stats

# Chạy verification
stats = verify_data_structure()
```

---

## 📊 BƯỚC 8: XEM PERFORMANCE REPORT

### Cell 7: Load và hiển thị metrics

```python
# Load metrics từ file
with open('performance_metrics.json', 'r') as f:
    metrics = json.load(f)

print("=" * 70)
print("📈 FINAL PERFORMANCE REPORT")
print("   (Copy vào Report.docx)")
print("=" * 70)

print("\n🎯 TESTBED:")
print(f"   {metrics['testbed']}")

print("\n⏱️  RUNNING TIME (Wall Time - End-to-End):")
print(f"   • Total: {metrics['total_wall_time_seconds']:.2f}s")
print(f"           ({metrics['total_wall_time_minutes']:.2f} min)")
print(f"           ({metrics['total_wall_time_hours']:.2f} hours)")
print(f"   • Papers processed: {metrics['papers_processed']}")
print(f"   • Avg per paper: {metrics['avg_time_per_paper']:.2f}s")

print("\n💾 MEMORY FOOTPRINT:")
print(f"   • Maximum RAM: {metrics['max_ram_mb']:.2f} MB ({metrics['max_ram_gb']:.2f} GB)")
print(f"   • Disk increase: {metrics['disk_increase_mb']:.2f} MB ({metrics['disk_increase_gb']:.2f} GB)")
print(f"   • Output size: {metrics['output_size_mb']:.2f} MB ({metrics['output_size_gb']:.2f} GB)")

if stats:
    print("\n📊 DATA STATISTICS:")
    print(f"   • Total papers: {stats['total_papers']}")
    print(f"   • With TeX sources: {stats['papers_with_tex']}")
    print(f"   • With metadata: {stats['papers_with_metadata']}")
    print(f"   • With references: {stats['papers_with_references']}")
    print(f"   • Total versions: {stats['total_versions']}")
    print(f"   • Total .tex files: {stats['total_tex_files']}")
    print(f"   • Total .bib files: {stats['total_bib_files']}")

print("\n" + "=" * 70)
```

---

## 📥 BƯỚC 9: DOWNLOAD DỮ LIỆU

### Option 1: Download trực tiếp (file < 100MB)

```python
import shutil
from google.colab import files

# Nén dữ liệu
print("📦 Đang nén dữ liệu...")
shutil.make_archive('23127240_data', 'zip', '.', '23127240_data')

# Check size
size_mb = os.path.getsize('23127240_data.zip') / (1024**2)
print(f"✅ Đã tạo: 23127240_data.zip")
print(f"📊 Kích thước: {size_mb:.2f} MB")

if size_mb > 100:
    print("\n⚠️  File > 100MB, khuyến nghị upload lên Google Drive")
    print("   👉 Chạy cell tiếp theo")
else:
    print("\n⬇️  Downloading...")
    files.download('23127240_data.zip')
```

### Option 2: Upload to Google Drive (file lớn)

```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Copy to Drive
!cp 23127240_data.zip /content/drive/MyDrive/
!cp performance_metrics.json /content/drive/MyDrive/

print("✅ Đã upload lên Google Drive:")
print("   - 23127240_data.zip")
print("   - performance_metrics.json")
```

---

## 🎬 CHO DEMO VIDEO (≤120 GIÂY)

Khi quay video demo, bao gồm:

### 1. Setup (15s)
- Mở Colab, show Runtime = CPU-only
- Clone repo

### 2. Running (45s)
- Chạy scraper
- Show logs: downloading, extracting, removing figures
- Show memory tracking

### 3. Results (45s)
- Show performance metrics
- Verify data structure
- Show 1 paper mẫu (tex/, metadata.json, references.json)

### 4. Voice explanation:
- "Scraper chạy trên Colab CPU-only theo yêu cầu Lab 1"
- "Tự động đo wall time end-to-end và memory footprint"
- "Remove figures để giảm kích thước"
- "Crawl references từ Semantic Scholar"

---

## ⚠️ TROUBLESHOOTING

### Lỗi "ModuleNotFoundError: No module named 'main'":

**Nguyên nhân**: File `main.py` không tồn tại hoặc có tên khác trong thư mục `src/`

**Giải pháp 1**: Kiểm tra tên file thực tế
```python
%cd /content/ScrapingData/23127240/src
!ls -la *.py
```

Sau đó thay `main.py` bằng tên file đúng.

**Giải pháp 2**: Chạy trực tiếp bằng terminal (KHUYẾN NGHỊ)
```python
%cd /content/ScrapingData/23127240/src
# Thay 'main.py' bằng tên file thực tế
!python3 main.py
```

**Giải pháp 3**: Nếu repository không có file main
```python
# Clone lại repository mới nhất
%cd /content
!rm -rf ScrapingData
!git clone https://github.com/nhutphansayhi/ScrapingData.git
%cd ScrapingData/23127240
```

### Lỗi Rate Limit (429):
```python
# Đợi 5 phút
import time
time.sleep(300)
```

### Lỗi Disk Full:
```python
# Xóa cache
!rm -rf ~/.cache/
!rm -rf /tmp/*
```

### Script chạy quá lâu:
- Giảm số lượng papers trong config.py
- Hoặc chia nhỏ range

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Check logs trong cell scraper
2. Xem performance_metrics.json
3. Liên hệ: hlhdang@fit.hcmus.edu.vn

---

## ✅ CHECKLIST TRƯỚC KHI NỘP

- [ ] Runtime = CPU-only
- [ ] Scraper chạy thành công
- [ ] Performance metrics đã lưu
- [ ] Data structure đúng format (tex/, metadata.json, references.json)
- [ ] Figures đã được xóa
- [ ] Đã download/backup dữ liệu
- [ ] Report.docx đã ghi metrics
- [ ] Video demo ≤120s đã quay

---

**Chúc bạn thành công! 🚀**
