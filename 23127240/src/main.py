"""
Main arXiv scraper script
Student ID: 23127240
"""

import os
import sys
import time
import json
import argparse
import logging
import shutil
import psutil
import csv
from pathlib import Path

from config import (
    STUDENT_ID, START_YEAR_MONTH, START_ID,
    END_YEAR_MONTH, END_ID, DATA_DIR, LOGS_DIR
)
from utils import (
    setup_logging, format_arxiv_id, format_folder_name,
    ensure_dir, get_directory_size
)
from arxiv_scraper import ArxivScraper
from reference_scraper import ReferenceScraper
from reference_scraper_optimized import OptimizedReferenceScraper
from bibtex_generator import BibtexGenerator

logger = logging.getLogger(__name__)


class ArxivScraperPipeline:
    
    def __init__(self, output_dir: str, use_batch: bool = True):
        self.output_dir = output_dir
        self.use_batch = use_batch
        ensure_dir(output_dir)
        
        self.arxiv_scraper = ArxivScraper(output_dir)
        
        if use_batch:
            self.reference_scraper = OptimizedReferenceScraper(batch_size=500)
            logger.info("Using OPTIMIZED batch reference scraper (up to 500x faster!)")
        else:
            self.reference_scraper = ReferenceScraper()
            logger.info("Using standard reference scraper")
        
        self.bibtex_generator = BibtexGenerator()
        
        self.stats = {
            'total_papers': 0,
            'successful_papers': 0,
            'failed_papers': 0,
            'total_runtime': 0.0,
            'paper_runtimes': [],
            'paper_sizes_before': [],
            'paper_sizes_after': [],
            'reference_counts': [],
            'reference_success_counts': [],
            'discovery_time': 0.0,
            'max_ram_mb': 0.0,
            'avg_ram_mb': 0.0,
            'ram_samples': [],
            'max_disk_mb': 0.0,
            'final_disk_mb': 0.0
        }
        
        # Detailed paper tracking for CSV
        self.paper_details = []
        
        self.process = psutil.Process()
        self.initial_ram = self.process.memory_info().rss / (1024 * 1024)
    
    def get_completed_papers(self) -> set:
        """Get set of paper IDs that have already been scraped successfully"""
        completed = set()
        if not os.path.exists(self.output_dir):
            return completed
        
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            if os.path.isdir(item_path):
                # Check if paper has metadata.json and references.json (signs of completion)
                metadata_file = os.path.join(item_path, "metadata.json")
                references_file = os.path.join(item_path, "references.json")
                
                if os.path.exists(metadata_file) and os.path.exists(references_file):
                    # Convert folder name back to arxiv_id format (e.g., "2311-14685" -> "2311.14685")
                    arxiv_id = item.replace('-', '.')
                    completed.add(arxiv_id)
        
        return completed
    
    def get_attempted_papers(self) -> set:
        """Get set of ALL paper IDs that have been attempted (have any folder)"""
        attempted = set()
        if not os.path.exists(self.output_dir):
            return attempted
        
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            # Check if it's a directory and looks like a paper folder (format: YYMM-NNNNN)
            if os.path.isdir(item_path) and '-' in item:
                # Convert folder name back to arxiv_id format (e.g., "2311-14685" -> "2311.14685")
                arxiv_id = item.replace('-', '.')
                attempted.add(arxiv_id)
        
        return attempted
    
    def load_checkpoint_stats(self, completed_papers: set):
        """Load statistics from checkpoint to preserve previous progress
        
        Returns:
            set: arxiv_ids of papers already in CSV (to skip during scraping)
        """
        stats_file = os.path.join(self.output_dir, "scraping_stats.json")
        details_csv = os.path.join(self.output_dir, "paper_details.csv")
        csv_papers = set()
        
        # Load paper details from CSV if exists
        if os.path.exists(details_csv):
            try:
                with open(details_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Convert numeric fields
                        row['paper_id'] = int(row['paper_id'])
                        row['runtime_s'] = float(row['runtime_s'])
                        row['size_before'] = int(row['size_before'])
                        row['size_after'] = int(row['size_after'])
                        row['size_before_figures'] = int(row['size_before_figures'])
                        row['size_after_figures'] = int(row['size_after_figures'])
                        row['num_refs'] = int(row['num_refs'])
                        row['current_output_size'] = int(row['current_output_size'])
                        row['max_rss'] = float(row['max_rss'])
                        row['avg_rss'] = float(row['avg_rss'])
                        self.paper_details.append(row)
                        # Track arxiv_id to skip this paper
                        csv_papers.add(row['arxiv_id'])
                logger.info(f"Loaded {len(self.paper_details)} paper details from checkpoint")
            except Exception as e:
                logger.warning(f"Failed to load paper details from CSV: {e}")
        
        if not os.path.exists(stats_file):
            # No checkpoint file, count manually from completed papers
            logger.info("No checkpoint file found, counting from completed papers...")
            self.stats['successful_papers'] = len(completed_papers)
            return
        
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                saved_stats = json.load(f)
            
            # Restore key statistics
            data_stats = saved_stats.get('data_statistics', {})
            perf_time = saved_stats.get('performance_running_time', {})
            perf_mem = saved_stats.get('performance_memory_footprint', {})
            
            self.stats['successful_papers'] = data_stats.get('successful_papers', len(completed_papers))
            self.stats['failed_papers'] = data_stats.get('failed_papers', 0)
            self.stats['max_ram_mb'] = perf_mem.get('max_ram_mb', 0.0)
            self.stats['avg_ram_mb'] = perf_mem.get('avg_ram_mb', 0.0)
            self.stats['max_disk_mb'] = perf_mem.get('max_disk_storage_mb', 0.0)
            
            # Load arrays if available (for accurate averaging)
            # These won't be in JSON, so we'll rebuild from completed papers
            logger.info(f"Loaded checkpoint: {self.stats['successful_papers']} successful, {self.stats['failed_papers']} failed")
            
        except Exception as e:
            logger.warning(f"Failed to load checkpoint stats: {e}")
            self.stats['successful_papers'] = len(completed_papers)
        
        return csv_papers
    
    def update_memory_stats(self):
        current_ram = self.process.memory_info().rss / (1024 * 1024)
        self.stats['ram_samples'].append(current_ram)
        if current_ram > self.stats['max_ram_mb']:
            self.stats['max_ram_mb'] = current_ram
    
    def update_disk_stats(self):
        if os.path.exists(self.output_dir):
            disk_usage = get_directory_size(self.output_dir) / (1024 * 1024)
            if disk_usage > self.stats['max_disk_mb']:
                self.stats['max_disk_mb'] = disk_usage
    
    def generate_paper_ids(self, start_ym: str, start_id: int, 
                          end_ym: str, end_id: int) -> list:
        """
        Generate paper IDs for the range.
        For 23127240: 2311.14685 to 2312.00843
        - Month 2311: 14685 to 18840 (4156 papers)
        - Month 2312: 00001 to 00843 (843 papers)  ← BẮT ĐẦU TỪ 1, KHÔNG PHẢI 0
        Total: 4999 papers
        """
        paper_ids = []
        
        start_ym_int = int(start_ym)
        end_ym_int = int(end_ym)
        
        # Same month case
        if start_ym_int == end_ym_int:
            ym_str = str(start_ym_int)
            for paper_id in range(start_id, end_id + 1):
                arxiv_id = format_arxiv_id(ym_str, paper_id)
                paper_ids.append(arxiv_id)
            return paper_ids
        
        # Multi-month case: calculate end ID for first month
        # Total papers in last month = end_id (starting from 1, not 0)
        total_in_last_month = end_id
        
        # Calculate how many papers we need from first month
        TARGET_TOTAL = 5000  # 4156 + 844 = 5000
        papers_needed_from_first_month = TARGET_TOTAL - total_in_last_month
        first_month_end_id = start_id + papers_needed_from_first_month - 1
        
        # Generate papers for first month
        ym_str = str(start_ym_int)
        for paper_id in range(start_id, first_month_end_id + 1):
            arxiv_id = format_arxiv_id(ym_str, paper_id)
            paper_ids.append(arxiv_id)
        
        # Generate papers for last month (from 1 to end_id, NOT from 0)
        ym_str = str(end_ym_int)
        for paper_id in range(1, end_id + 1):  # BẮT ĐẦU TỪ 1
            arxiv_id = format_arxiv_id(ym_str, paper_id)
            paper_ids.append(arxiv_id)
        
        return paper_ids
    
    def scrape_single_paper(self, arxiv_id: str) -> bool:
        start_time = time.time()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing paper {arxiv_id}")
        logger.info(f"{'='*60}")
        
        folder_name = format_folder_name(arxiv_id)
        paper_dir = os.path.join(self.output_dir, folder_name)
        ensure_dir(paper_dir)
        
        size_before = get_directory_size(paper_dir) if os.path.exists(paper_dir) else 0
        
        success = self.arxiv_scraper.scrape_paper(arxiv_id, paper_dir)
        
        if not success:
            logger.error(f"Failed to scrape paper {arxiv_id}")
            self.stats['failed_papers'] += 1
            return False
        
        size_after = get_directory_size(paper_dir)
        self.stats['paper_sizes_before'].append(size_before)
        self.stats['paper_sizes_after'].append(size_after)
        
        self.update_memory_stats()
        self.update_disk_stats()
        
        metadata_path = os.path.join(paper_dir, "metadata.json")
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            self.stats['failed_papers'] += 1
            return False
        
        # NOTE: NO references.bib at paper level!
        # BibTeX files (.bib) should ONLY exist inside tex/<yymm-id>vX/ folders
        # Those are the ORIGINAL .bib files uploaded by authors
        
        # Scrape references from Semantic Scholar
        references_path = os.path.join(paper_dir, "references.json")
        ref_before = self.reference_scraper.get_stats()['total_references']
        self.reference_scraper.scrape_references(arxiv_id, references_path)
        ref_after = self.reference_scraper.get_stats()['total_references']
        
        num_refs = 0
        try:
            with open(references_path, 'r', encoding='utf-8') as f:
                references = json.load(f)
                num_refs = len(references)
                self.stats['reference_counts'].append(num_refs)
                self.stats['reference_success_counts'].append(ref_after - ref_before)
        except:
            self.stats['reference_counts'].append(0)
            self.stats['reference_success_counts'].append(0)
        
        runtime = time.time() - start_time
        self.stats['paper_runtimes'].append(runtime)
        self.stats['successful_papers'] += 1
        
        # Get current memory usage
        current_ram = self.process.memory_info().rss / (1024 * 1024)
        current_disk = get_directory_size(self.output_dir) / (1024 * 1024)
        avg_ram = sum(self.stats['ram_samples']) / len(self.stats['ram_samples']) if self.stats['ram_samples'] else current_ram
        
        # Save detailed paper info
        paper_detail = {
            'paper_id': self.stats['successful_papers'],
            'arxiv_id': arxiv_id,
            'title': metadata.get('title', 'N/A'),
            'authors': ', '.join(metadata.get('authors', [])),
            'runtime_s': round(runtime, 2),
            'size_before': size_before,
            'size_after': size_after,
            'size_before_figures': size_before,  # Before removing figures
            'size_after_figures': size_after,    # After removing figures
            'num_refs': num_refs,
            'current_output_size': int(current_disk * 1024 * 1024),  # bytes
            'max_rss': round(self.stats['max_ram_mb'], 2),
            'avg_rss': round(avg_ram, 2),
            'processed_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.paper_details.append(paper_detail)
        
        logger.info(f"Successfully processed {arxiv_id} in {runtime:.2f}s")
        logger.info(f"Paper size: {size_after / 1024:.2f} KB")
        
        return True
    
    def run(self, start_ym: str = None, start_id: int = None,
            end_ym: str = None, end_id: int = None):
        start_ym = start_ym or START_YEAR_MONTH
        start_id = start_id if start_id is not None else START_ID
        end_ym = end_ym or END_YEAR_MONTH
        end_id = end_id if end_id is not None else END_ID
        
        logger.info("="*80)
        logger.info("arXiv Scraper Pipeline Started")
        logger.info(f"Student ID: {STUDENT_ID}")
        logger.info(f"Range: {start_ym}.{start_id:05d} to {end_ym}.{end_id:05d}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("="*80)
        
        pipeline_start = time.time()
        
        logger.info("\nGenerating paper IDs...")
        discovery_start = time.time()
        paper_ids = self.generate_paper_ids(start_ym, start_id, end_ym, end_id)
        self.stats['discovery_time'] = time.time() - discovery_start
        
        # IMPORTANT: total_papers always = original count (not remaining)
        original_total = len(paper_ids)
        self.stats['total_papers'] = original_total
        
        # Check for papers that have been attempted (any folder exists)
        attempted_papers = self.get_attempted_papers()
        completed_papers = self.get_completed_papers()
        
        # Always load checkpoint stats from completed papers only
        csv_papers = self.load_checkpoint_stats(completed_papers)
        
        if attempted_papers:
            logger.info(f"Found {len(attempted_papers)} papers already attempted (have folders)")
        if completed_papers:
            logger.info(f"Found {len(completed_papers)} successfully completed (with metadata+references)")
        if csv_papers:
            logger.info(f"Found {len(csv_papers)} papers already tracked in CSV")
        
        # Skip ALL attempted papers (whether successful or failed)
        papers_to_skip = attempted_papers
        if papers_to_skip:
            logger.info(f"Total papers to skip: {len(papers_to_skip)}")
            logger.info("These papers will be skipped (already attempted)")
            
            # Filter out attempted papers
            paper_ids = [pid for pid in paper_ids if pid not in papers_to_skip]
            logger.info(f"Remaining papers to scrape: {len(paper_ids)}")
        
        logger.info(f"Total papers in assignment: {original_total}")
        logger.info(f"Papers to process now: {len(paper_ids)}")
        if paper_ids:
            logger.info(f"First paper: {paper_ids[0]}")
            logger.info(f"Last paper: {paper_ids[-1]}")
        
        for i, arxiv_id in enumerate(paper_ids, 1):
            logger.info(f"\n[{i}/{len(paper_ids)}] Processing {arxiv_id}")
            
            try:
                self.scrape_single_paper(arxiv_id)
            except Exception as e:
                logger.error(f"Unexpected error processing {arxiv_id}: {e}")
                self.stats['failed_papers'] += 1
            
            # Print progress và save stats mỗi 10 papers
            if i % 10 == 0:
                self.print_progress()
                # Save intermediate stats để không mất dữ liệu nếu crash
                self.save_stats(intermediate=True)
            
            # Save stats mỗi 50 papers (full save)
            if i % 50 == 0:
                logger.info(f"💾 Checkpoint: Saving full statistics at paper {i}/{len(paper_ids)}")
                self.save_stats(intermediate=False)
        
        self.cleanup_all_temp_files()
        
        self.stats['total_runtime'] = time.time() - pipeline_start
        if self.stats['ram_samples']:
            self.stats['avg_ram_mb'] = sum(self.stats['ram_samples']) / len(self.stats['ram_samples'])
        self.stats['final_disk_mb'] = get_directory_size(self.output_dir) / (1024 * 1024)
        
        self.print_final_stats()
        self.save_stats()
    
    def print_progress(self):
        logger.info("\n" + "="*60)
        logger.info("PROGRESS UPDATE")
        logger.info(f"Successful: {self.stats['successful_papers']}")
        logger.info(f"Failed: {self.stats['failed_papers']}")
        logger.info(f"Success rate: {self.stats['successful_papers']/max(1, self.stats['successful_papers']+self.stats['failed_papers'])*100:.1f}%")
        logger.info("="*60 + "\n")
    
    def cleanup_all_temp_files(self):
        logger.info("\nCleaning up temporary files...")
        temp_cleaned = 0
        
        if not os.path.exists(self.output_dir):
            return
        
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            if os.path.isdir(item_path):
                temp_dir = os.path.join(item_path, "temp")
                if os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                        temp_cleaned += 1
                        logger.debug(f"Removed temp directory: {temp_dir}")
                    except Exception as e:
                        logger.warning(f"Failed to remove temp directory {temp_dir}: {e}")
        
        if temp_cleaned > 0:
            logger.info(f"Cleaned {temp_cleaned} temp directories")
        else:
            logger.info("No temp directories found")
    
    def print_final_stats(self):
        logger.info("\n" + "="*80)
        logger.info("FINAL STATISTICS")
        logger.info("="*80)
        
        logger.info(f"\n1. Scraping Results:")
        logger.info(f"  Total papers attempted: {self.stats['total_papers']}")
        logger.info(f"  Successful: {self.stats['successful_papers']}")
        logger.info(f"  Failed: {self.stats['failed_papers']}")
        success_rate = self.stats['successful_papers']/max(1, self.stats['total_papers'])*100
        logger.info(f"  Overall success rate: {success_rate:.2f}%")
        
        if self.stats['paper_sizes_before'] and self.stats['paper_sizes_after']:
            avg_before = sum(self.stats['paper_sizes_before']) / len(self.stats['paper_sizes_before'])
            avg_after = sum(self.stats['paper_sizes_after']) / len(self.stats['paper_sizes_after'])
            logger.info(f"\n2. Paper Size Statistics:")
            logger.info(f"  Average size before removing figures: {avg_before:.2f} bytes ({avg_before/1024:.2f} KB)")
            logger.info(f"  Average size after removing figures: {avg_after:.2f} bytes ({avg_after/1024:.2f} KB)")
            reduction = ((avg_before - avg_after) / avg_before * 100) if avg_before > 0 else 0
            logger.info(f"  Size reduction: {reduction:.1f}%")
        
        if self.stats['reference_counts']:
            avg_refs = sum(self.stats['reference_counts']) / len(self.stats['reference_counts'])
            logger.info(f"\n3. Reference Statistics:")
            logger.info(f"  Average references per paper: {avg_refs:.2f}")
            
            ref_stats = self.reference_scraper.get_stats()
            if ref_stats['papers_queried'] > 0:
                ref_success_rate = (ref_stats['papers_found'] / ref_stats['papers_queried']) * 100
                logger.info(f"  Papers queried for references: {ref_stats['papers_queried']}")
                logger.info(f"  Papers found: {ref_stats['papers_found']}")
                logger.info(f"  Total references found: {ref_stats['total_references']}")
                logger.info(f"  References with arXiv ID: {ref_stats['references_with_arxiv_id']}")
                logger.info(f"  Reference metadata success rate: {ref_success_rate:.2f}%")
        
        logger.info(f"\n4. Performance - Running Time:")
        logger.info(f"  Total runtime (wall time): {self.stats['total_runtime']:.2f}s ({self.stats['total_runtime']/60:.2f} min)")
        logger.info(f"  Entry discovery time: {self.stats['discovery_time']:.2f}s")
        if self.stats['paper_runtimes']:
            avg_runtime = sum(self.stats['paper_runtimes']) / len(self.stats['paper_runtimes'])
            logger.info(f"  Average time per paper: {avg_runtime:.2f}s")
            total_processing = sum(self.stats['paper_runtimes'])
            logger.info(f"  Total paper processing time: {total_processing:.2f}s ({total_processing/60:.2f} min)")
        
        logger.info(f"\n5. Performance - Memory Footprint:")
        logger.info(f"  Maximum RAM used: {self.stats['max_ram_mb']:.2f} MB")
        logger.info(f"  Average RAM consumption: {self.stats['avg_ram_mb']:.2f} MB")
        logger.info(f"  Maximum disk storage required: {self.stats['max_disk_mb']:.2f} MB")
        logger.info(f"  Final output storage size: {self.stats['final_disk_mb']:.2f} MB")
        
        arxiv_stats = self.arxiv_scraper.get_stats()
        logger.info(f"\n6. Additional ArXiv Statistics:")
        logger.info(f"  Total versions downloaded: {arxiv_stats['versions_downloaded']}")
        logger.info(f"  Total download time: {arxiv_stats['total_download_time']:.2f}s")
        
        logger.info("\n" + "="*80)
    
    def save_stats(self, intermediate=False):
        """
        Save statistics to JSON and CSV
        
        Args:
            intermediate: If True, only save JSON (faster). If False, save both JSON and CSV.
        """
        stats_file = os.path.join(self.output_dir, "scraping_stats.json")
        
        all_stats = {
            'student_id': STUDENT_ID,
            'paper_range': {
                'start': f"{START_YEAR_MONTH}.{START_ID:05d}",
                'end': f"{END_YEAR_MONTH}.{END_ID:05d}"
            },
            'data_statistics': {
                'total_papers': self.stats['total_papers'],
                'successful_papers': self.stats['successful_papers'],
                'failed_papers': self.stats['failed_papers'],
                'overall_success_rate': f"{self.stats['successful_papers']/max(1, self.stats['total_papers'])*100:.2f}%",
                'avg_paper_size_before_bytes': sum(self.stats['paper_sizes_before']) / len(self.stats['paper_sizes_before']) if self.stats['paper_sizes_before'] else 0,
                'avg_paper_size_after_bytes': sum(self.stats['paper_sizes_after']) / len(self.stats['paper_sizes_after']) if self.stats['paper_sizes_after'] else 0,
                'avg_references_per_paper': sum(self.stats['reference_counts']) / len(self.stats['reference_counts']) if self.stats['reference_counts'] else 0,
                'reference_metadata_success_rate': f"{(self.reference_scraper.get_stats()['papers_found'] / max(1, self.reference_scraper.get_stats()['papers_queried'])) * 100:.2f}%"
            },
            'performance_running_time': {
                'total_runtime_seconds': round(self.stats['total_runtime'], 2),
                'total_runtime_minutes': round(self.stats['total_runtime'] / 60, 2),
                'entry_discovery_time_seconds': round(self.stats['discovery_time'], 2),
                'average_time_per_paper_seconds': round(sum(self.stats['paper_runtimes']) / len(self.stats['paper_runtimes']), 2) if self.stats['paper_runtimes'] else 0,
                'total_paper_processing_time_seconds': round(sum(self.stats['paper_runtimes']), 2) if self.stats['paper_runtimes'] else 0
            },
            'performance_memory_footprint': {
                'max_ram_mb': round(self.stats['max_ram_mb'], 2),
                'avg_ram_mb': round(self.stats['avg_ram_mb'], 2),
                'max_disk_storage_mb': round(self.stats['max_disk_mb'], 2),
                'final_output_storage_mb': round(self.stats['final_disk_mb'], 2)
            },
            'arxiv_statistics': self.arxiv_scraper.get_stats(),
            'reference_statistics': self.reference_scraper.get_stats()
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(all_stats, f, indent=2)
        
        if not intermediate:
            logger.info(f"\nStatistics saved to: {stats_file}")
        
        # Also save CSV format for report (only on full save to avoid overhead)
        if not intermediate:
            self.save_stats_csv()
            self.save_paper_details_csv()
    
    def save_stats_csv(self):
        """Save statistics in CSV format for easy import into reports"""
        csv_file = os.path.join(self.output_dir, "scraping_stats.csv")
        
        # Calculate stats
        avg_size_before = sum(self.stats['paper_sizes_before']) / len(self.stats['paper_sizes_before']) if self.stats['paper_sizes_before'] else 0
        avg_size_after = sum(self.stats['paper_sizes_after']) / len(self.stats['paper_sizes_after']) if self.stats['paper_sizes_after'] else 0
        avg_refs = sum(self.stats['reference_counts']) / len(self.stats['reference_counts']) if self.stats['reference_counts'] else 0
        avg_runtime_per_paper = sum(self.stats['paper_runtimes']) / len(self.stats['paper_runtimes']) if self.stats['paper_runtimes'] else 0
        
        ref_stats = self.reference_scraper.get_stats()
        ref_success_rate = (ref_stats['papers_found'] / max(1, ref_stats['papers_queried'])) * 100
        
        rows = [
            ['Metric Category', 'Metric Name', 'Value', 'Unit'],
            ['', '', '', ''],
            ['General Info', 'Student ID', STUDENT_ID, ''],
            ['General Info', 'Paper Range Start', f"{START_YEAR_MONTH}.{START_ID:05d}", ''],
            ['General Info', 'Paper Range End', f"{END_YEAR_MONTH}.{END_ID:05d}", ''],
            ['', '', '', ''],
            ['Data Statistics', 'Total Papers Attempted', self.stats['total_papers'], 'papers'],
            ['Data Statistics', 'Successful Papers', self.stats['successful_papers'], 'papers'],
            ['Data Statistics', 'Failed Papers', self.stats['failed_papers'], 'papers'],
            ['Data Statistics', 'Overall Success Rate', f"{self.stats['successful_papers']/max(1, self.stats['total_papers'])*100:.2f}", '%'],
            ['Data Statistics', 'Avg Paper Size Before (removing figures)', f"{avg_size_before:.2f}", 'bytes'],
            ['Data Statistics', 'Avg Paper Size Before (removing figures)', f"{avg_size_before/1024:.2f}", 'KB'],
            ['Data Statistics', 'Avg Paper Size After (removing figures)', f"{avg_size_after:.2f}", 'bytes'],
            ['Data Statistics', 'Avg Paper Size After (removing figures)', f"{avg_size_after/1024:.2f}", 'KB'],
            ['Data Statistics', 'Size Reduction', f"{((avg_size_before - avg_size_after) / max(1, avg_size_before) * 100):.2f}", '%'],
            ['Data Statistics', 'Avg References Per Paper', f"{avg_refs:.2f}", 'references'],
            ['Data Statistics', 'Papers Queried for References', ref_stats['papers_queried'], 'papers'],
            ['Data Statistics', 'Papers Found with References', ref_stats['papers_found'], 'papers'],
            ['Data Statistics', 'Total References Found', ref_stats['total_references'], 'references'],
            ['Data Statistics', 'References with arXiv ID', ref_stats['references_with_arxiv_id'], 'references'],
            ['Data Statistics', 'Reference Metadata Success Rate', f"{ref_success_rate:.2f}", '%'],
            ['', '', '', ''],
            ['Performance - Running Time', 'Total Runtime (Wall Time)', f"{self.stats['total_runtime']:.2f}", 'seconds'],
            ['Performance - Running Time', 'Total Runtime (Wall Time)', f"{self.stats['total_runtime']/60:.2f}", 'minutes'],
            ['Performance - Running Time', 'Entry Discovery Time', f"{self.stats['discovery_time']:.2f}", 'seconds'],
            ['Performance - Running Time', 'Avg Time Per Paper', f"{avg_runtime_per_paper:.2f}", 'seconds'],
            ['Performance - Running Time', 'Total Paper Processing Time', f"{sum(self.stats['paper_runtimes']):.2f}", 'seconds'],
            ['Performance - Running Time', 'Total Paper Processing Time', f"{sum(self.stats['paper_runtimes'])/60:.2f}", 'minutes'],
            ['', '', '', ''],
            ['Performance - Memory Footprint', 'Maximum RAM Used', f"{self.stats['max_ram_mb']:.2f}", 'MB'],
            ['Performance - Memory Footprint', 'Average RAM Consumption', f"{self.stats['avg_ram_mb']:.2f}", 'MB'],
            ['Performance - Memory Footprint', 'Maximum Disk Storage Required', f"{self.stats['max_disk_mb']:.2f}", 'MB'],
            ['Performance - Memory Footprint', 'Final Output Storage Size', f"{self.stats['final_disk_mb']:.2f}", 'MB'],
            ['Performance - Memory Footprint', 'Final Output Storage Size', f"{self.stats['final_disk_mb']/1024:.2f}", 'GB'],
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        logger.info(f"CSV statistics saved to: {csv_file}")
    
    def save_paper_details_csv(self):
        """Save detailed per-paper statistics to CSV"""
        csv_file = os.path.join(self.output_dir, "paper_details.csv")
        
        if not self.paper_details:
            logger.warning("No paper details to save")
            return
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['paper_id', 'arxiv_id', 'title', 'authors', 'runtime_s', 
                         'size_before', 'size_after', 'size_before_figures', 'size_after_figures',
                         'num_refs', 'current_output_size', 'max_rss', 'avg_rss', 'processed_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(self.paper_details)
        
        logger.info(f"Paper details CSV saved to: {csv_file} ({len(self.paper_details)} papers)")


def main():
    parser = argparse.ArgumentParser(description='arXiv Paper Scraper')
    parser.add_argument('--start-ym', type=str, help='Start year-month (e.g., 2311)')
    parser.add_argument('--start-id', type=int, help='Start paper ID')
    parser.add_argument('--end-ym', type=str, help='End year-month (e.g., 2312)')
    parser.add_argument('--end-id', type=int, help='End paper ID')
    parser.add_argument('--output', type=str, default=DATA_DIR, help='Output directory')
    parser.add_argument('--no-batch', action='store_true', help='Disable batch API optimization')
    
    args = parser.parse_args()
    
    setup_logging(LOGS_DIR)
    
    use_batch = not args.no_batch
    
    pipeline = ArxivScraperPipeline(args.output, use_batch=use_batch)
    pipeline.run(
        start_ym=args.start_ym,
        start_id=args.start_id,
        end_ym=args.end_ym,
        end_id=args.end_id
    )
    
    logger.info("\nScraping completed!")


if __name__ == "__main__":
    main()
