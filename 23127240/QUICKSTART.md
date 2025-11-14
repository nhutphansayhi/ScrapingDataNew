# Quick Start Guide

## For Local Development

### 1. Setup (One-time)

```bash
# Navigate to project directory
cd 23127240/src

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Test the Scraper

```bash
# Run test script (interactive)
python test_scraper.py

# Or test manually with small range
python main.py --start-ym 2208 --start-id 11941 --end-ym 2208 --end-id 11943
```

### 3. Run Full Scraper

```bash
# Run with default settings (full assignment range)
python main.py

# This will scrape: 2208.11941 to 2209.11937
# Output will be in: ../23127240_data/
# Logs will be in: ./logs/scraper.log
```

### 4. Check Results

```bash
# View statistics
cat ../23127240_data/scraping_stats.json

# Check logs
cat logs/scraper.log

# List scraped papers
ls ../23127240_data/
```

## For Google Colab

### 1. Upload Files

Upload the entire `23127240` folder to your Google Drive or Colab session.

### 2. Run in Colab

```python
# Install dependencies
!pip install arxiv==2.1.0 requests==2.31.0 pandas==2.0.3

# Navigate to source directory
%cd /content/23127240/src

# Test with small range first
!python main.py --start-ym 2208 --start-id 11941 --end-ym 2208 --end-id 11943

# Run full scraper
!python main.py
```

### 3. Download Results

```python
# Compress results
!cd .. && zip -r 23127240_data.zip 23127240_data/

# Download the zip file
from google.colab import files
files.download('../23127240_data.zip')
```

## Expected Output Structure

```
23127240_data/
├── 2208-11941/
│   ├── tex/
│   │   ├── v1/
│   │   │   ├── main.tex
│   │   │   └── ...
│   │   └── v2/ (if exists)
│   ├── metadata.json
│   ├── references.bib
│   └── references.json
├── 2208-11942/
│   └── ...
└── scraping_stats.json
```

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Permission denied"
```bash
# Make sure you have write permissions in the output directory
mkdir -p ../23127240_data
```

### "Rate limit exceeded"
The scraper automatically handles rate limits with delays. Just wait and it will continue.

### "Paper not found"
Some arXiv IDs in the range may not exist - this is normal. The scraper will log these and continue.

## Performance Tips

- **First run**: Test with 3-5 papers to ensure everything works
- **Full run**: Can take 2-4 hours for ~100 papers (due to API rate limits)
- **Monitoring**: Use `tail -f logs/scraper.log` to watch progress in real-time
- **Resume**: If interrupted, re-run the script - it will skip existing papers

## Time Estimates

- **Single paper**: ~10-15 seconds
- **10 papers**: ~2-3 minutes  
- **100 papers**: ~20-30 minutes
- **1000 papers**: ~3-5 hours

*Note: Time depends on API response times and number of versions per paper*

