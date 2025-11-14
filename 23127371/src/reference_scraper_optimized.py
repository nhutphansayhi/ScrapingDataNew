"""
Optimized reference scraper using Semantic Scholar Batch API
"""

import time
import json
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime

from config import (
    SEMANTIC_SCHOLAR_API_BASE,
    SEMANTIC_SCHOLAR_FIELDS,
    SEMANTIC_SCHOLAR_DELAY,
    MAX_RETRIES,
    RETRY_DELAY
)

logger = logging.getLogger(__name__)


class OptimizedReferenceScraper:
    
    def __init__(self, batch_size: int = 500):
        self.api_base = SEMANTIC_SCHOLAR_API_BASE
        self.session = requests.Session()
        self.batch_size = batch_size
        self.stats = {
            'papers_queried': 0,
            'papers_found': 0,
            'papers_not_found': 0,
            'total_references': 0,
            'references_with_arxiv_id': 0,
            'api_errors': 0,
            'batch_requests': 0
        }
    
    def get_papers_batch(self, arxiv_ids: List[str]) -> Dict[str, Optional[List[Dict]]]:
        self.stats['batch_requests'] += 1
        
        url = f"{self.api_base}/paper/batch"
        params = {"fields": SEMANTIC_SCHOLAR_FIELDS}
        
        paper_ids = [f"arXiv:{arxiv_id}" for arxiv_id in arxiv_ids]
        data = {"ids": paper_ids}
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.post(url, params=params, json=data, timeout=60)
                
                if response.status_code == 200:
                    results = response.json()
                    
                    papers_data = {}
                    for i, paper_data in enumerate(results):
                        arxiv_id = arxiv_ids[i]
                        
                        if paper_data is None:
                            self.stats['papers_not_found'] += 1
                            papers_data[arxiv_id] = None
                            logger.warning(f"Paper {arxiv_id} not found in batch")
                        else:
                            self.stats['papers_found'] += 1
                            references = paper_data.get("references", [])
                            self.stats['total_references'] += len(references)
                            papers_data[arxiv_id] = references
                            logger.debug(f"Found {len(references)} references for {arxiv_id}")
                    
                    self.stats['papers_queried'] += len(arxiv_ids)
                    logger.info(f"Batch request successful: {len(arxiv_ids)} papers, {sum(len(r) if r else 0 for r in papers_data.values())} total references")
                    
                    time.sleep(SEMANTIC_SCHOLAR_DELAY)
                    return papers_data
                
                elif response.status_code == 429:
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        wait_time = int(retry_after)
                    else:
                        wait_time = min(60 * (attempt + 1), 300)
                    
                    logger.warning(f"Batch rate limit (attempt {attempt + 1}/{MAX_RETRIES}), waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    logger.warning(f"Batch attempt {attempt + 1}/{MAX_RETRIES}: HTTP {response.status_code}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                
            except Exception as e:
                logger.warning(f"Batch attempt {attempt + 1}/{MAX_RETRIES}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
        
        self.stats['api_errors'] += 1
        logger.error(f"Batch request failed after {MAX_RETRIES} attempts for {len(arxiv_ids)} papers")
        return {arxiv_id: None for arxiv_id in arxiv_ids}
    
    def extract_arxiv_references(self, references: List[Dict]) -> Dict[str, Dict]:
        arxiv_references = {}
        
        for ref in references:
            external_ids = ref.get('externalIds', {})
            if not external_ids or 'ArXiv' not in external_ids:
                continue
            
            arxiv_id = external_ids['ArXiv']
            
            metadata = {
                'title': ref.get('title', ''),
                'authors': [author.get('name', '') for author in ref.get('authors', [])],
                'submission_date': ref.get('publicationDate', ''),
                'semantic_scholar_id': ref.get('paperId', '')
            }
            
            try:
                if '.' in arxiv_id:
                    parts = arxiv_id.split('.')
                    formatted_id = f"{parts[0]}-{parts[1]}"
                else:
                    formatted_id = arxiv_id
                
                arxiv_references[formatted_id] = metadata
                self.stats['references_with_arxiv_id'] += 1
                
            except Exception as e:
                logger.warning(f"Failed to format arXiv ID {arxiv_id}: {e}")
        
        return arxiv_references
    
    def scrape_references(self, arxiv_id: str, output_path: str) -> bool:
        logger.info(f"Scraping references for {arxiv_id}...")
        
        try:
            references = self.get_paper_references(arxiv_id)
            
            if references is None:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2, ensure_ascii=False)
                logger.warning(f"No references found for {arxiv_id}, saved empty file")
                return False
            
            total_refs = len(references)
            logger.info(f"Found {total_refs} total references for {arxiv_id}")
            
            arxiv_references = self.extract_arxiv_references(references)
            arxiv_refs_count = len(arxiv_references)
            
            if total_refs > 0 and arxiv_refs_count == 0:
                logger.warning(f"Paper {arxiv_id} has {total_refs} references but none have arXiv IDs")
            elif arxiv_refs_count > 0:
                logger.info(f"Extracted {arxiv_refs_count} references with arXiv IDs from {total_refs} total")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(arxiv_references, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(arxiv_references)} arXiv references to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scrape references for {arxiv_id}: {e}")
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2, ensure_ascii=False)
            except Exception as write_error:
                logger.error(f"Failed to create references.json: {write_error}")
            return False
    
    def get_paper_references(self, arxiv_id: str) -> Optional[List[Dict]]:
        batch_result = self.get_papers_batch([arxiv_id])
        return batch_result.get(arxiv_id)
    
    def scrape_references_batch(self, arxiv_papers: Dict[str, str]) -> Dict[str, bool]:
        if not arxiv_papers:
            return {}
        
        arxiv_ids = list(arxiv_papers.keys())
        results = {}
        
        for i in range(0, len(arxiv_ids), self.batch_size):
            batch_ids = arxiv_ids[i:i + self.batch_size]
            batch_count = len(batch_ids)
            
            logger.info(f"Processing batch {i//self.batch_size + 1}: {batch_count} papers")
            
            batch_results = self.get_papers_batch(batch_ids)
            
            for arxiv_id in batch_ids:
                output_path = arxiv_papers[arxiv_id]
                references = batch_results.get(arxiv_id)
                
                try:
                    if references is None:
                        with open(output_path, 'w', encoding='utf-8') as f:
                            json.dump({}, f, indent=2, ensure_ascii=False)
                        results[arxiv_id] = False
                    else:
                        arxiv_references = self.extract_arxiv_references(references)
                        with open(output_path, 'w', encoding='utf-8') as f:
                            json.dump(arxiv_references, f, indent=2, ensure_ascii=False)
                        results[arxiv_id] = True
                except Exception as e:
                    logger.error(f"Failed to save references for {arxiv_id}: {e}")
                    results[arxiv_id] = False
        
        return results
    
    def get_stats(self) -> Dict:
        return self.stats.copy()
