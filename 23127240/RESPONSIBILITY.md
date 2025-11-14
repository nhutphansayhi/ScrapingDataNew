# Project Responsibility Documentation

**Project**: arXiv Paper Scraper - Lab 1  
**Student ID**: 23127240  
**Last Updated**: November 14, 2025

---

## 📂 Project Structure Overview

```
23127240/
├── src/                              # Core source code
├── 23127240_data/                    # Output data (excluded from git)
├── documentation/                    # Project documentation
└── configuration files               # Setup files
```

---

## 🎯 Core Source Files (`src/`)

### 1. **`main.py`** - Main Pipeline Controller
**Responsibility**: Orchestrates the entire scraping workflow

**Key Functions**:
- `ArxivScraperPipeline.__init__()` - Initialize scraper components
- `scrape_paper()` - Process single paper (metadata + source + references)
- `scrape_papers_in_range()` - Batch processing with progress tracking
- `resume_scraping()` - Resume interrupted scraping sessions

**Integrates**:
- `ArxivScraper` for paper download
- `OptimizedReferenceScraper` for batch reference fetching
- `BibtexGenerator` for BibTeX file creation
- Performance monitoring (wall time, RAM, disk usage)

**Output**: 
- `paper_details.csv` - Per-paper metrics
- `scraping_stats.json` - Overall statistics
- Terminal progress display

---

### 2. **`arxiv_scraper.py`** - arXiv API Interaction
**Responsibility**: Handle all arXiv API calls and source downloads

**Key Functions**:
- `get_paper_metadata()` - Fetch paper metadata (title, authors, abstract, etc.)
- `download_source()` - Download .tar.gz source files
- `scrape_paper()` - Complete paper processing pipeline

**Key Features**:
- Retry mechanism for failed downloads (max 3 attempts)
- Fallback to direct e-print endpoint if library fails
- API rate limiting (3s delay between requests)
- TeX source extraction and validation

**External APIs**:
- arXiv API: `http://export.arxiv.org/api/query`
- arXiv e-print: `https://arxiv.org/e-print/{arxiv_id}`

---

### 3. **`reference_scraper.py`** - Standard Reference Scraper
**Responsibility**: Fetch paper references one-by-one

**Key Functions**:
- `get_paper_references()` - Query Semantic Scholar for single paper
- `save_references()` - Save to JSON file

**Limitations**:
- Sequential processing (slow for large batches)
- 1 request per paper
- Replaced by `reference_scraper_optimized.py` in production

**Use Case**: Backup/fallback scraper

---

### 4. **`reference_scraper_optimized.py`** - Batch Reference Scraper
**Responsibility**: High-performance batch reference fetching

**Key Functions**:
- `get_references_batch()` - Fetch up to 500 papers at once
- `process_papers()` - Batch processing with automatic chunking

**Performance**:
- **500x faster** than sequential scraper
- Batch size: 500 papers per request
- Rate limiting: 1.1s between batches
- Automatic retry on rate limit (429 errors)

**External API**:
- Semantic Scholar Batch API: `POST /graph/v1/paper/batch`

---

### 5. **`bibtex_generator.py`** - BibTeX File Creation
**Responsibility**: Generate BibTeX files from scraped references

**Key Functions**:
- `generate_bibtex_entry()` - Create single BibTeX entry
- `create_bibtex_file()` - Generate complete .bib file

**Input**: `references.json`  
**Output**: `references.bib`

**Format**:
```bibtex
@article{FirstAuthor2023Title,
  author = {...},
  title = {...},
  journal = {arXiv},
  year = {2023},
  ...
}
```

---

### 6. **`utils.py`** - Utility Functions
**Responsibility**: Common helper functions across modules

**Key Functions**:

**File Operations**:
- `extract_tar_gz()` - Extract .tar.gz archives
- `process_tex_files()` - Find main .tex and .bib files
- `clean_version_folder()` - Remove figures to reduce size

**Formatting**:
- `format_arxiv_id()` - Convert to arXiv ID format (e.g., "2311.14685")
- `format_folder_name()` - Convert to folder name (e.g., "2311-14685")
- `sanitize_filename()` - Clean filenames for filesystem

**Monitoring**:
- `get_directory_size()` - Calculate folder size
- `clean_temp_files()` - Remove temporary extraction files

**Figure Removal**:
- Removes: `.png`, `.jpg`, `.jpeg`, `.pdf`, `.eps`, `.gif`
- Keeps: `.tex`, `.bib`, `.sty`, `.cls`, `.bst`

---

### 7. **`config.py`** - Configuration Settings
**Responsibility**: Central configuration for entire project

**Key Settings**:

**Student Info**:
```python
STUDENT_ID = "23127240"
```

**Paper Range** (Lab 1 requirement):
```python
START_YEAR_MONTH = "2311"
START_ID = 14685
END_YEAR_MONTH = "2312"
END_ID = 844
# Total: ~5000 papers
```

**API Rate Limits**:
```python
ARXIV_API_DELAY = 3.0          # 3s between arXiv requests
SEMANTIC_SCHOLAR_DELAY = 1.1   # 1.1s between S2 batch requests
MAX_RETRIES = 3
RETRY_DELAY = 5.0
```

**Paths**:
```python
DATA_DIR = "../23127240_data"
LOGS_DIR = "./logs"
```

---

## 🛠️ Utility Scripts

### 8. **`backfill_paper_details.py`** - Data Recovery
**Responsibility**: Regenerate `paper_details.csv` from existing data

**Use Case**: 
- Scraping was interrupted before CSV saved
- CSV file corrupted or deleted
- Need to recalculate statistics

**Process**:
1. Scan all paper folders in `23127240_data/`
2. Extract metadata from `metadata.json`
3. Count references from `references.json`
4. Reconstruct CSV with available data

---

### 9. **`retry_references.py`** - Reference Re-fetching
**Responsibility**: Retry failed reference downloads

**Use Case**:
- Papers missing `references.json`
- API rate limits during initial scraping
- Semantic Scholar API downtime

**Process**:
1. Find papers with `metadata.json` but no `references.json`
2. Batch fetch references using optimized scraper
3. Save to appropriate paper folders

---

### 10. **`test_scraper.py`** - Manual Testing
**Responsibility**: Test scraper on specific paper IDs

**Usage**:
```bash
python test_scraper.py 2311.14685 2311.14686
```

**Features**:
- Test single or multiple papers
- Verify download and extraction
- Check reference fetching
- Debug without full pipeline

---

### 11. **`test_source_url.py`** - URL Validation
**Responsibility**: Test arXiv source download URLs

**Use Case**: Debug download failures

---

## 📊 Output Data Structure

### `23127240_data/` Directory

```
23127240_data/
├── paper_details.csv           # Per-paper metrics (runtime, size, refs)
├── scraping_stats.json         # Overall statistics
├── scraping_stats.csv          # Stats in CSV format
└── 2311-14685/                 # Paper folder (format: YYMM-NNNNN)
    ├── tex/                    # TeX source files
    │   ├── main.tex           # Main document
    │   ├── references.bib     # Bibliography
    │   └── *.sty, *.cls       # Style files
    ├── metadata.json          # Paper metadata
    └── references.json        # Reference list
```

---

## 📄 Documentation Files

### 12. **`README.md`** - Project Overview
- Quick start guide
- Lab requirements summary
- Repository structure

### 13. **`QUICKSTART.md`** - 5-Minute Setup
- Minimal steps to run scraper
- Local and Colab instructions

### 14. **`COLAB_SCRAPING_GUIDE.md`** - Colab Deployment
- 8-step process for Google Colab
- Performance monitoring setup
- Troubleshooting section

### 15. **`HUONG_DAN_CHAY_COLAB_TU_DAU.md`** - Vietnamese Colab Guide
- Detailed Vietnamese instructions
- Cell-by-cell execution guide
- Alternative running methods (5A/5B/5C)

### 16. **`HUONG_DAN_NOP_BAI_DAY_DU.md`** - Submission Guide
- Complete submission workflow
- 3 submission locations: Moodle, Google Drive, YouTube
- Checklist and flowchart

### 17. **`PROJECT_SUMMARY.md`** - Technical Documentation
- Detailed architecture
- API integration details
- Performance optimization notes

### 18. **`START_HERE.md`** - Onboarding Guide
- New user orientation
- File navigation
- Recommended reading order

---

## 🎯 Execution Flow

### Normal Workflow:
```
1. config.py          → Load settings
2. main.py            → Initialize pipeline
3. arxiv_scraper.py   → Download papers
4. utils.py           → Extract & clean
5. reference_scraper_optimized.py → Fetch references (batch)
6. bibtex_generator.py → Create .bib files
7. main.py            → Save metrics & stats
```

### Resume Workflow:
```
1. main.py --resume   → Check existing papers
2. Skip processed papers
3. Continue from last incomplete paper
4. Update cumulative stats
```

---

## 🔧 Configuration & Setup Files

### 19. **`requirements.txt`** - Python Dependencies
```txt
arxiv
requests
beautifulsoup4
bibtexparser
psutil
```

### 20. **`.gitignore`** - Git Exclusions
Excludes:
- `23127240_data/` (scraped data)
- `__pycache__/` (Python cache)
- `.venv/` (virtual environments)
- `.DS_Store` (macOS files)

---

## 📈 Performance Monitoring

### Metrics Tracked:

**Wall Time**:
- Total runtime (end-to-end)
- Per-paper processing time
- Average time per paper

**Memory Footprint**:
- Maximum RAM usage
- Disk space increase
- Output data size

**Success Rate**:
- Papers attempted
- Papers successful
- Papers failed
- Download success rate

---

## 🚀 Key Features

1. **Batch Processing**: 500x faster reference fetching
2. **Resume Support**: Continue interrupted scraping
3. **Automatic Retry**: Handle API failures gracefully
4. **Figure Removal**: Reduce storage by ~70%
5. **Progress Tracking**: Real-time console updates
6. **Performance Monitoring**: CPU, RAM, disk usage
7. **Data Validation**: Verify complete downloads

---

## 📞 Support & Maintenance

**Primary Contact**: Student 23127240  
**Course**: Introduction to Data Science  
**Institution**: University of Science, VNU-HCMC  
**Instructor**: hlhdang@fit.hcmus.edu.vn

---

## 🔄 Version History

- **v1.0** (Nov 14, 2025): Initial implementation
  - Basic scraping pipeline
  - Sequential reference scraper
  
- **v2.0** (Nov 14, 2025): Performance optimization
  - Batch reference scraper (500x speedup)
  - Resume functionality
  - Enhanced monitoring

- **v3.0** (Nov 14, 2025): Colab deployment
  - GitHub repository setup
  - Comprehensive documentation
  - Multiple execution guides

---

**End of Responsibility Documentation**
