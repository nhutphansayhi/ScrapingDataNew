# arXiv Data Scraper - Lab 1 Introduction to Data Science

Student ID: **23127240**

## 📚 Overview

This repository contains the implementation for Lab 1 of the Introduction to Data Science course at University of Science, VNU-HCMC. The project scrapes arXiv papers including full TeX sources, metadata, and references.

## 🎯 Lab Requirements

- **Testbed**: Google Colab CPU-only mode
- **Metrics**: Wall time (end-to-end), Memory footprint (max RAM, disk usage)
- **Data**: TeX sources, metadata.json, references.json
- **Optimization**: Automatic figure removal to reduce size

## 🚀 Quick Start

### Option 1: Run on Google Colab (Recommended)

1. Open the Colab notebook: [ArXiv_Scraper_Colab.ipynb](23127371/ArXiv_Scraper_Colab.ipynb)
2. Or follow the detailed guide: [COLAB_SCRAPING_GUIDE.md](23127371/COLAB_SCRAPING_GUIDE.md)

### Option 2: Run Locally

```bash
git clone https://github.com/nhutphansayhi/ScrapingData.git
cd ScrapingData/23127371/src
pip install -r requirements.txt
python main.py
```

## 📁 Repository Structure

```
23127371/
├── src/                          # Source code
│   ├── main.py                   # Main scraper
│   ├── arxiv_scraper.py          # arXiv API interaction
│   ├── reference_scraper.py      # Semantic Scholar integration
│   ├── config.py                 # Configuration
│   └── requirements.txt          # Dependencies
├── ArXiv_Scraper_Colab.ipynb    # Ready-to-use Colab notebook
├── COLAB_SCRAPING_GUIDE.md      # Detailed Colab instructions
├── README.md                     # Project documentation
├── QUICKSTART.md                 # Quick start guide
└── Report.doc                    # Lab report
```

## 📊 Features

- ✅ Entry discovery via arXiv API
- ✅ Full TeX source download and extraction
- ✅ Automatic figure removal (png, jpg, pdf, eps)
- ✅ Reference crawling from Semantic Scholar
- ✅ Performance monitoring (wall time, RAM, disk)
- ✅ Retry mechanism for API rate limits
- ✅ Data validation and verification

## 📝 Documentation

- **[QUICKSTART.md](23127371/QUICKSTART.md)** - Get started in 5 minutes
- **[COLAB_SCRAPING_GUIDE.md](23127371/COLAB_SCRAPING_GUIDE.md)** - Complete Colab guide
- **[PROJECT_SUMMARY.md](23127371/PROJECT_SUMMARY.md)** - Technical details

## 🎓 Course Information

- **Course**: Introduction to Data Science
- **Lab**: Lab 1 - Data Scraping
- **Institution**: University of Science, VNU-HCMC
- **Instructor**: Huỳnh Lâm Hải Đăng

## 📧 Contact

For questions or issues, contact: hlhdang@fit.hcmus.edu.vn

---

**Last Updated**: November 2025
