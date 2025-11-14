"""
Test script for arXiv scraper - runs a small test on a few papers
Student ID: 23127371
"""

import os
import sys
import logging
from pathlib import Path

from utils import setup_logging
from main import ArxivScraperPipeline


def test_small_range():
    """Test scraper on a small range of papers"""
    
    print("="*80)
    print("arXiv Scraper - Test Mode")
    print("="*80)
    print()
    print("This will test the scraper on a small range: 2208.11941 to 2208.11943")
    print("Expected time: ~1-2 minutes")
    print()
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Test cancelled.")
        return
    
    # Setup
    setup_logging("./logs")
    test_output = "../23127371_test_data"
    
    # Create test pipeline
    print("\nInitializing test pipeline...")
    pipeline = ArxivScraperPipeline(test_output)
    
    # Run on small range
    print("Starting test scrape...")
    pipeline.run(
        start_ym="2208",
        start_id=11941,
        end_ym="2208",
        end_id=11943
    )
    
    print("\n" + "="*80)
    print("Test completed!")
    print(f"Check output in: {test_output}")
    print(f"Check logs in: ./logs/scraper.log")
    print("="*80)


def test_single_paper():
    """Test scraper on a single paper"""
    
    print("="*80)
    print("arXiv Scraper - Single Paper Test")
    print("="*80)
    print()
    
    arxiv_id = input("Enter arXiv ID to test (e.g., 2208.11941): ").strip()
    
    if not arxiv_id:
        print("No ID provided. Test cancelled.")
        return
    
    # Parse ID
    try:
        parts = arxiv_id.split('.')
        year_month = parts[0]
        paper_id = int(parts[1])
    except:
        print("Invalid arXiv ID format. Use format: YYMM.XXXXX (e.g., 2208.11941)")
        return
    
    # Setup
    setup_logging("./logs")
    test_output = "../23127371_test_data"
    
    # Create test pipeline
    print(f"\nTesting with paper: {arxiv_id}")
    pipeline = ArxivScraperPipeline(test_output)
    
    # Run on single paper
    pipeline.run(
        start_ym=year_month,
        start_id=paper_id,
        end_ym=year_month,
        end_id=paper_id
    )
    
    print("\n" + "="*80)
    print("Test completed!")
    print(f"Check output in: {test_output}")
    print("="*80)


def main():
    """Main test menu"""
    
    print()
    print("="*80)
    print("arXiv Scraper - Testing Utility")
    print("Student ID: 23127371")
    print("="*80)
    print()
    print("Choose a test option:")
    print("1. Test small range (3 papers: 2208.11941-11943)")
    print("2. Test single paper (enter custom arXiv ID)")
    print("3. Exit")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        test_small_range()
    elif choice == "2":
        test_single_paper()
    elif choice == "3":
        print("Exiting.")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()

