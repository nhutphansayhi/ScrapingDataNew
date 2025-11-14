"""
Script to backfill paper_details.csv with information from already scraped papers
"""

import os
import json
import csv
import time
from pathlib import Path
from config import STUDENT_ID, DATA_DIR
from utils import get_directory_size

def get_all_completed_papers(output_dir):
    """Get all completed papers from the output directory"""
    completed_papers = []
    
    if not os.path.exists(output_dir):
        return completed_papers
    
    for item in sorted(os.listdir(output_dir)):
        item_path = os.path.join(output_dir, item)
        if os.path.isdir(item_path):
            metadata_file = os.path.join(item_path, "metadata.json")
            references_file = os.path.join(item_path, "references.json")
            
            if os.path.exists(metadata_file) and os.path.exists(references_file):
                # Convert folder name to arxiv_id (e.g., "2311-14685" -> "2311.14685")
                arxiv_id = item.replace('-', '.')
                completed_papers.append((arxiv_id, item_path))
    
    return completed_papers

def extract_paper_details(arxiv_id, paper_dir, paper_id, total_output_size):
    """Extract details from a completed paper"""
    try:
        # Load metadata
        metadata_path = os.path.join(paper_dir, "metadata.json")
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Load references
        references_path = os.path.join(paper_dir, "references.json")
        with open(references_path, 'r', encoding='utf-8') as f:
            references = json.load(f)
        num_refs = len(references)
        
        # Get paper size (after figures removed)
        paper_size = get_directory_size(paper_dir)
        
        # Get modification time as processed_at
        try:
            mod_time = os.path.getmtime(metadata_path)
            processed_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
        except:
            processed_at = "N/A"
        
        detail = {
            'paper_id': paper_id,
            'arxiv_id': arxiv_id,
            'title': metadata.get('title', 'N/A'),
            'authors': ', '.join(metadata.get('authors', [])),
            'runtime_s': 0,  # Not available for old papers
            'size_before': 0,  # Not available
            'size_after': paper_size,
            'size_before_figures': 0,  # Not available
            'size_after_figures': paper_size,
            'num_refs': num_refs,
            'current_output_size': total_output_size,
            'max_rss': 0.0,  # Not available
            'avg_rss': 0.0,  # Not available
            'processed_at': processed_at
        }
        
        return detail
    except Exception as e:
        print(f"Error extracting details for {arxiv_id}: {e}")
        return None

def backfill_paper_details():
    """Backfill paper_details.csv with information from completed papers"""
    output_dir = DATA_DIR
    csv_file = os.path.join(output_dir, "paper_details.csv")
    
    print(f"Scanning directory: {output_dir}")
    
    # Get all completed papers
    completed_papers = get_all_completed_papers(output_dir)
    print(f"Found {len(completed_papers)} completed papers")
    
    if not completed_papers:
        print("No completed papers found!")
        return
    
    # Load existing paper_details if exists
    existing_arxiv_ids = set()
    if os.path.exists(csv_file):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_arxiv_ids.add(row['arxiv_id'])
            print(f"Found {len(existing_arxiv_ids)} papers already in CSV")
        except Exception as e:
            print(f"Warning: Could not read existing CSV: {e}")
    
    # Extract details for all papers
    all_details = []
    total_output_size = get_directory_size(output_dir)
    
    print("\nExtracting paper details...")
    for i, (arxiv_id, paper_dir) in enumerate(completed_papers, 1):
        if arxiv_id in existing_arxiv_ids:
            print(f"[{i}/{len(completed_papers)}] Skipping {arxiv_id} (already in CSV)")
            continue
        
        print(f"[{i}/{len(completed_papers)}] Processing {arxiv_id}")
        detail = extract_paper_details(arxiv_id, paper_dir, i, total_output_size)
        if detail:
            all_details.append(detail)
    
    if not all_details:
        print("\nNo new papers to add to CSV!")
        return
    
    # Read existing details if file exists
    if os.path.exists(csv_file):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_details = list(reader)
                # Convert to dict format
                for row in existing_details:
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
                all_details = existing_details + all_details
        except Exception as e:
            print(f"Warning: Could not merge with existing CSV: {e}")
    
    # Re-number paper_ids sequentially
    for i, detail in enumerate(all_details, 1):
        detail['paper_id'] = i
    
    # Write to CSV
    fieldnames = ['paper_id', 'arxiv_id', 'title', 'authors', 'runtime_s', 
                 'size_before', 'size_after', 'size_before_figures', 'size_after_figures',
                 'num_refs', 'current_output_size', 'max_rss', 'avg_rss', 'processed_at']
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_details)
    
    print(f"\n✅ Successfully backfilled paper_details.csv!")
    print(f"   Total papers in CSV: {len(all_details)}")
    print(f"   File location: {csv_file}")

if __name__ == "__main__":
    backfill_paper_details()
