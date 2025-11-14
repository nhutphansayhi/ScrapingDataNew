STUDENT_ID = "23127240"

START_YEAR_MONTH = "2311"
START_ID = 14685
END_YEAR_MONTH = "2312"
END_ID = 844

ARXIV_API_DELAY = 1.5
SEMANTIC_SCHOLAR_DELAY = 0.6

MAX_RETRIES = 3
RETRY_DELAY = 3.0

DATA_DIR = f"../{STUDENT_ID}_data"
LOGS_DIR = "./logs"

MAX_FILE_SIZE = 100 * 1024 * 1024

SEMANTIC_SCHOLAR_API_BASE = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_FIELDS = "references,references.paperId,references.externalIds,references.title,references.authors,references.publicationDate,references.year"

