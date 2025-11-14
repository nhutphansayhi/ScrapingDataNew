"""
Script to retry scraping references for papers with empty references.json files
"""

import os
import json
import logging
from pathlib import Path

from config import DATA_DIR
from reference_scraper import ReferenceScraper
from utils import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def find_empty_references(data_dir: str) -> list:
    """
    Find all papers with empty references.json files
    
    Args:
        data_dir: Data directory path
    
    Returns:
        List of arXiv IDs with empty references
    """
    empty_papers = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return empty_papers
    
    # Iterate through all paper folders
    for folder in data_path.iterdir():
        if not folder.is_dir():
            continue
        
        # Check if folder name matches pattern (e.g., "2208-12041")
        folder_name = folder.name
        if '-' not in folder_name:
            continue
        
        # Check for references.json file
        ref_file = folder / "references.json"
        if not ref_file.exists():
            logger.info(f"Found paper {folder_name} without references.json")
            empty_papers.append(folder_name)
            continue
        
        # Check if file is empty or has no references
        try:
            with open(ref_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not data or len(data) == 0:
                    logger.info(f"Found paper {folder_name} with empty references.json")
                    empty_papers.append(folder_name)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in {ref_file}, will retry")
            empty_papers.append(folder_name)
        except Exception as e:
            logger.error(f"Error reading {ref_file}: {e}")
    
    return empty_papers


def retry_references(arxiv_id_folder: str, data_dir: str):
    """
    Retry scraping references for a paper
    
    Args:
        arxiv_id_folder: Folder name (e.g., "2208-12041")
        data_dir: Data directory path
    """
    # Convert folder name to arXiv ID format (e.g., "2208-12041" -> "2208.12041")
    if '-' in arxiv_id_folder:
        arxiv_id = arxiv_id_folder.replace('-', '.')
    else:
        arxiv_id = arxiv_id_folder
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Retrying references for {arxiv_id}")
    logger.info(f"{'='*60}")
    
    # Path to references.json
    ref_path = os.path.join(data_dir, arxiv_id_folder, "references.json")
    
    # Initialize reference scraper
    ref_scraper = ReferenceScraper()
    
    # Scrape references
    success = ref_scraper.scrape_references(arxiv_id, ref_path)
    
    if success:
        # Check result
        try:
            with open(ref_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data and len(data) > 0:
                    logger.info(f"✓ Successfully scraped {len(data)} references for {arxiv_id}")
                else:
                    logger.warning(f"⚠ Scraped but no arXiv references found for {arxiv_id}")
        except Exception as e:
            logger.error(f"Error reading result for {arxiv_id}: {e}")
    else:
        logger.error(f"✗ Failed to scrape references for {arxiv_id}")


def main():
    """Main function"""
    logger.info("="*60)
    logger.info("Retry References Scraper")
    logger.info("="*60)
    
    # Find all papers with empty references
    empty_papers = find_empty_references(DATA_DIR)
    
    if not empty_papers:
        logger.info("No papers with empty references found!")
        return
    
    logger.info(f"\nFound {len(empty_papers)} papers with empty references:")
    for paper in empty_papers:
        logger.info(f"  - {paper}")
    
    # Ask for confirmation
    print(f"\nFound {len(empty_papers)} papers with empty references.")
    print("Do you want to retry scraping references for all of them? (y/n): ", end='')
    response = input().strip().lower()
    
    if response != 'y':
        logger.info("Cancelled by user")
        return
    
    # Retry references for each paper
    logger.info(f"\nRetrying references for {len(empty_papers)} papers...")
    for i, paper_folder in enumerate(empty_papers, 1):
        logger.info(f"\n[{i}/{len(empty_papers)}] Processing {paper_folder}")
        try:
            retry_references(paper_folder, DATA_DIR)
        except Exception as e:
            logger.error(f"Error processing {paper_folder}: {e}")
    
    logger.info("\n" + "="*60)
    logger.info("Retry completed!")
    logger.info("="*60)


if __name__ == "__main__":
    main()

