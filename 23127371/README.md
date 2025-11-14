# arXiv Paper Scraper - Student ID: 23127240

This project scrapes arXiv papers including full TeX sources, metadata, BibTeX references, and citation information using Semantic Scholar API.

## Assignment Details

**Student ID:** 23127240  
**Paper Range:** 2023-11/14685 to 2023-12/00843  
**Course:** Introduction to Data Science - Milestone 1

## Features

- Downloads all versions of arXiv papers (v1, v2, v3, ...)
- Extracts TeX source files with automatic figure removal
- Generates metadata in JSON format
- Creates BibTeX reference files
- Crawls citation information using Semantic Scholar API
- Filters references to include only papers with arXiv IDs

## Environment Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for API access

### Installation

1. **Clone or extract the project**
   ```bash
   cd 23127371
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

## Running the Scraper

### Basic Usage

To run the scraper with default settings (range from config.py):

```bash
python main.py
```

This will scrape papers from **2311.14685** to **2312.00843** as specified in the assignment.

### Advanced Usage

You can customize the scraping range:

```bash
python main.py --start-ym 2311 --start-id 14685 --end-ym 2312 --end-id 843
```

### Command-Line Arguments

- `--start-ym`: Start year-month (format: YYMM, e.g., "2311" for November 2023)
- `--start-id`: Start paper ID number (e.g., 14685)
- `--end-ym`: End year-month (format: YYMM, e.g., "2312" for December 2023)
- `--end-id`: End paper ID number (e.g., 843)
- `--output`: Output directory path (default: `../23127240_data`)

### Example Commands

```bash
python main.py

python main.py --start-ym 2311 --start-id 14685 --end-ym 2311 --end-id 14690

python main.py --output ./my_data
```

## Output Structure

The scraper creates the following directory structure:

```
23127240_data/
├── 2311-14685/
│   ├── tex/
│   │   ├── v1/
│   │   ├── v2/
│   │   └── ...
│   ├── metadata.json
│   ├── references.bib
│   └── references.json
├── 2311-14686/
│   └── ...
└── scraping_stats.json   # Overall scraping statistics
```

### File Descriptions

1. **tex/** - Contains all versions of the paper's TeX source files with figures removed
2. **metadata.json** - Paper metadata including title, authors, submission date, revised dates, abstract, categories, DOI, journal reference
3. **references.bib** - BibTeX entry for the paper
4. **references.json** - Dictionary of references that have arXiv IDs with metadata

## Processing Details

### Figure Removal

The scraper automatically removes figures from TeX files to reduce storage size by removing `\includegraphics` commands, `\begin{figure}...\end{figure}` environments, and deleting image files.

### API Rate Limits

The scraper respects API rate limits with 3 seconds delay between arXiv requests and 1.1 seconds delay between Semantic Scholar requests.

### Error Handling

Automatic retry up to 3 attempts for failed requests, graceful handling of missing papers, and detailed logging of all operations.

## Logging

Logs are saved to `logs/scraper.log` with progress updates, download status, error messages, and performance statistics.

## Statistics Tracking

The scraper tracks comprehensive statistics as required:

### Data Statistics
- Number of papers scraped successfully
- Overall success rate
- Average paper size before and after removing figures
- Average number of references per paper
- Average success rate for scraping reference metadata

### Performance Metrics

#### Running Time
- Total runtime (wall time)
- Entry discovery time
- Average time to process each paper
- Total paper processing time

#### Memory Footprint
- Maximum RAM used during scraping
- Average RAM consumption
- Maximum disk storage required
- Final output storage size

All statistics are saved to `scraping_stats.json` in the output directory.

## Performance Notes

- **Runtime**: Approximately 10-15 seconds per paper
- **Storage**: Each paper typically uses 50-500 KB after figure removal
- **Memory**: Peak usage around 200-300 MB

## Troubleshooting

### Common Issues

1. **"Paper not found" errors** - Some arXiv IDs may not exist, scraper continues with other papers
2. **Rate limit errors** - Automatically handled with delays
3. **Connection timeouts** - Automatic retry for failed requests
4. **Import errors** - Ensure all packages installed: `pip install -r requirements.txt`

### Testing on Google Colab

To run the scraper on Google Colab:

```python
!pip install arxiv requests sickle pandas psutil

!python main.py
```

## System Requirements

- **Python**: 3.8 or higher
- **Disk Space**: At least 1 GB free
- **RAM**: Minimum 2 GB recommended
- **Network**: Stable internet connection

## License

This project is created for educational purposes as part of the Introduction to Data Science course.

## Contact

**Student ID:** 23127240

