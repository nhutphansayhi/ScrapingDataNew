"""
arXiv paper scraper module
"""

import os
import time
import json
import logging
import arxiv
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from utils import (
    format_arxiv_id, format_folder_name, extract_tar_gz,
    process_tex_files, clean_version_folder, ensure_dir, clean_temp_files
)
from config import ARXIV_API_DELAY, MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)


class ArxivScraper:
    """Scraper for arXiv papers"""
    
    def __init__(self, output_dir: str):
        """
        Initialize arXiv scraper
        
        Args:
            output_dir: Base directory for output
        """
        self.output_dir = output_dir
        self.client = arxiv.Client()
        self.stats = {
            'papers_attempted': 0,
            'papers_successful': 0,
            'papers_failed': 0,
            'versions_downloaded': 0,
            'total_download_time': 0.0,
            'total_processing_time': 0.0
        }
    
    def get_paper_metadata(self, arxiv_id: str) -> Optional[Dict]:
        """
        Get metadata for a paper
        
        Args:
            arxiv_id: arXiv ID (e.g., "2208.11941")
        
        Returns:
            Metadata dictionary or None if failed
        """
        for attempt in range(MAX_RETRIES):
            try:
                search = arxiv.Search(id_list=[arxiv_id])
                paper = next(self.client.results(search))
                
                # Extract metadata
                # Note: revised_dates will be populated later when downloading all versions
                # publication_venue can be from journal_ref or comment field
                publication_venue = paper.journal_ref if paper.journal_ref else (
                    paper.comment if paper.comment and any(
                        keyword in paper.comment.lower() 
                        for keyword in ['conference', 'workshop', 'published', 'accepted', 'journal', 'proceedings']
                    ) else None
                )
                
                metadata = {
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'submission_date': paper.published.isoformat() if paper.published else None,
                    'revised_dates': [],  # Will be populated from all versions
                    'publication_venue': publication_venue,  # Required by Lab 1
                    'abstract': paper.summary,
                    'categories': paper.categories,
                    'primary_category': paper.primary_category,
                    'doi': paper.doi,
                    'journal_ref': paper.journal_ref,
                    'arxiv_id': arxiv_id,
                    'pdf_url': paper.pdf_url,
                    'comment': paper.comment
                }
                
                logger.info(f"Retrieved metadata for {arxiv_id}: {paper.title}")
                return metadata
                
            except StopIteration:
                logger.warning(f"Paper {arxiv_id} not found")
                return None
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {arxiv_id}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
        
        logger.error(f"Failed to get metadata for {arxiv_id} after {MAX_RETRIES} attempts")
        return None
    
    def download_source(self, arxiv_id: str, version: str, output_dir: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Download source files for a specific version
        
        Args:
            arxiv_id: arXiv ID without version
            version: Version string (e.g., "v1")
            output_dir: Directory to save source
        
        Returns:
            Tuple of (success, tar_path, updated_date)
        """
        versioned_id = f"{arxiv_id}{version}"
        
        for attempt in range(MAX_RETRIES):
            try:
                search = arxiv.Search(id_list=[versioned_id])
                paper = next(self.client.results(search))
                
                # Get updated date for this version
                updated_date = paper.updated.isoformat() if paper.updated else None
                
                # Extract year-month and paper number from arxiv_id for source URL
                # Format: YYMM.nnnnn -> YYMM/nnnnn
                parts = arxiv_id.split('.')
                if len(parts) == 2:
                    year_month = parts[0]  # e.g., "2208"
                    paper_num = parts[1]   # e.g., "12396"
                else:
                    # Fallback: try to extract from versioned_id
                    parts = versioned_id.replace('v', '.').split('.')
                    if len(parts) >= 2:
                        year_month = parts[0]
                        paper_num = parts[1]
                    else:
                        year_month = arxiv_id[:4]
                        paper_num = arxiv_id[5:].replace('v', '')
                
                # Download source
                temp_dir = os.path.join(output_dir, "temp")
                ensure_dir(temp_dir)
                
                tar_filename = f"{versioned_id}.tar.gz"
                tar_path = os.path.join(temp_dir, tar_filename)
                
                logger.info(f"Downloading source for {versioned_id}...")
                start_time = time.time()
                
                # Try using arxiv library's download_source() first
                downloaded = False
                try:
                    paper.download_source(dirpath=temp_dir, filename=tar_filename)
                    downloaded = True
                    logger.info(f"Downloaded {versioned_id} via arxiv library")
                except Exception as download_err:
                    error_str = str(download_err)
                    logger.debug(f"arxiv library download_source() failed: {download_err}, trying direct download")
                
                # If library method failed, try direct download from arXiv e-print endpoint
                if not downloaded:
                    # The correct arXiv source URL format is:
                    # https://arxiv.org/e-print/{versioned_id}
                    # This automatically returns the .tar.gz file
                    source_urls = [
                        f"https://arxiv.org/e-print/{versioned_id}",  # Primary URL
                        f"https://arxiv.org/src/{versioned_id}",      # Alternative URL
                    ]
                    
                    for source_url in source_urls:
                        logger.debug(f"Attempting direct download from: {source_url}")
                        try:
                            response = requests.get(source_url, timeout=60, stream=True, allow_redirects=True)
                            
                            if response.status_code == 200:
                                # Check if it's actually a tar.gz file
                                content_type = response.headers.get('Content-Type', '')
                                
                                # Check for HTML response (indicates paper has no source)
                                if 'html' in content_type.lower():
                                    logger.debug(f"Skipping {source_url} (HTML response, paper may not have source)")
                                    continue
                                
                                # Verify it's a gzip file by checking magic number
                                content = b''
                                for chunk in response.iter_content(chunk_size=8192):
                                    content += chunk
                                
                                # Check gzip magic number at the start
                                if len(content) < 2 or not content.startswith(b'\x1f\x8b'):
                                    logger.debug(f"Skipping {source_url} (not a gzip file)")
                                    continue
                                
                                # Save file
                                with open(tar_path, 'wb') as f:
                                    f.write(content)
                                
                                logger.info(f"Downloaded {versioned_id} via direct URL: {source_url}")
                                downloaded = True
                                break
                                
                            elif response.status_code == 404:
                                logger.debug(f"404 for {source_url}, trying next URL...")
                                continue
                            else:
                                logger.debug(f"HTTP {response.status_code} for {source_url}, trying next URL...")
                                continue
                                
                        except Exception as url_err:
                            logger.debug(f"Error downloading from {source_url}: {url_err}, trying next URL...")
                            continue
                    
                    if not downloaded:
                        logger.warning(f"Paper {versioned_id} does not have source files available (only PDF). "
                                     f"This paper will be skipped as it requires TeX source files.")
                        return False, None, None
                
                download_time = time.time() - start_time
                
                # Verify file was downloaded
                if not os.path.exists(tar_path) or os.path.getsize(tar_path) == 0:
                    raise Exception(f"Downloaded file is empty or doesn't exist: {tar_path}")
                
                self.stats['total_download_time'] += download_time
                logger.info(f"Downloaded {versioned_id} in {download_time:.2f}s")
                
                time.sleep(ARXIV_API_DELAY)
                return True, tar_path, updated_date
                
            except StopIteration:
                logger.warning(f"Version {versioned_id} not found")
                return False, None, None
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {versioned_id}: {error_msg}")
                
                # Check if it's a NoneType error - paper may not have source files
                if "'NoneType' object has no attribute 'replace'" in error_msg or "NoneType" in error_msg:
                    logger.warning(f"Paper {versioned_id} may not have source files available (only PDF)")
                    # Don't retry for this specific error
                    return False, None, None
                
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
        
        logger.error(f"Failed to download {versioned_id} after {MAX_RETRIES} attempts")
        return False, None, None
    
    def scrape_paper(self, arxiv_id: str, paper_dir: str) -> bool:
        """
        Scrape a single paper with all versions
        
        Args:
            arxiv_id: arXiv ID (e.g., "2208.11941")
            paper_dir: Directory for this paper's data
        
        Returns:
            True if successful, False otherwise
        """
        self.stats['papers_attempted'] += 1
        logger.info(f"Scraping paper {arxiv_id}...")
        
        start_time = time.time()
        temp_dir = os.path.join(paper_dir, "temp")
        
        try:
            # Get metadata
            metadata = self.get_paper_metadata(arxiv_id)
            if not metadata:
                self.stats['papers_failed'] += 1
                return False
            
            time.sleep(ARXIV_API_DELAY)
            
            # Create directories
            ensure_dir(paper_dir)
            tex_dir = os.path.join(paper_dir, "tex")
            ensure_dir(tex_dir)
            
            # Try to download versions (start with v1, try up to v10)
            versions_downloaded = 0
            revised_dates = []  # Collect all revised dates from versions
            
            for v in range(1, 11):
                version = f"v{v}"
                success, tar_path, updated_date = self.download_source(arxiv_id, version, paper_dir)
                
                if not success:
                    if v == 1:
                        # No v1 means paper doesn't exist
                        logger.error(f"No v1 found for {arxiv_id}")
                        self.stats['papers_failed'] += 1
                        return False
                    else:
                        # No more versions
                        break
                
                # Collect revised date (skip v1 as it's the submission date)
                if updated_date and v > 1:
                    if updated_date not in revised_dates:
                        revised_dates.append(updated_date)
                
                # Extract source
                # IMPORTANT: Version folder MUST follow format <yymm-id>v<version>
                # Example: 2311-14685v1, NOT just v1
                folder_name = format_folder_name(arxiv_id)  # "2311-14685"
                version_folder = f"{folder_name}{version}"   # "2311-14685v1"
                version_dir = os.path.join(tex_dir, version_folder)
                ensure_dir(version_dir)
                
                if extract_tar_gz(tar_path, version_dir):
                    # Process TeX files to remove figures
                    process_stats = process_tex_files(version_dir)
                    logger.info(f"Processed {process_stats['processed']} TeX files, "
                              f"removed {process_stats['images_removed']} image files")
                    
                    # CLEAN: Keep ONLY paper.tex and references.bib
                    clean_stats = clean_version_folder(version_dir)
                    logger.info(f"Cleaned version folder: kept {clean_stats['kept_tex']} .tex, "
                              f"{clean_stats['kept_bib']} .bib, removed {clean_stats['removed']} other files")
                    
                    versions_downloaded += 1
                    self.stats['versions_downloaded'] += 1
                
                # Clean up tar file immediately
                if os.path.exists(tar_path):
                    try:
                        os.remove(tar_path)
                        logger.debug(f"Removed tar file: {tar_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove tar file {tar_path}: {e}")
            
            if versions_downloaded == 0:
                logger.error(f"No versions downloaded for {arxiv_id}")
                self.stats['papers_failed'] += 1
                return False
            
            # Update metadata with all revised dates
            metadata['revised_dates'] = sorted(revised_dates)
            
            # Save metadata
            metadata_path = os.path.join(paper_dir, "metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            processing_time = time.time() - start_time
            self.stats['total_processing_time'] += processing_time
            self.stats['papers_successful'] += 1
            
            logger.info(f"Successfully scraped {arxiv_id} ({versions_downloaded} versions) in {processing_time:.2f}s")
            return True
            
        finally:
            # Always clean temp directory, even if error occurs
            if os.path.exists(temp_dir):
                clean_temp_files(temp_dir)
                logger.debug(f"Cleaned temp directory: {temp_dir}")
    
    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        return self.stats.copy()

