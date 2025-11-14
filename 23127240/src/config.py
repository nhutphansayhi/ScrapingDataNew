"""
Configuration file for arXiv scraper
"""

STUDENT_ID = "23127240"

# Paper range for Lab 1
# Month 11/2023: 2311.14685 → 2311.18840 (4156 papers)
# Month 12/2023: 2312.00001 → 2312.00844 (844 papers)
# Total: 5000 papers
START_YEAR_MONTH = "2311"
START_ID = 14685
END_YEAR_MONTH = "2312"
END_ID = 844

ARXIV_API_DELAY = 3.0
SEMANTIC_SCHOLAR_DELAY = 1.1

MAX_RETRIES = 3
RETRY_DELAY = 5.0

DATA_DIR = f"../{STUDENT_ID}_data"
LOGS_DIR = "./logs"

MAX_FILE_SIZE = 100 * 1024 * 1024

SEMANTIC_SCHOLAR_API_BASE = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_FIELDS = "references,references.paperId,references.externalIds,references.title,references.authors,references.publicationDate,references.year"

