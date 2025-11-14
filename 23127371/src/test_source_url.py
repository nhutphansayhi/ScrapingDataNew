"""Test script to check if arXiv paper has source files"""
import requests
import sys

arxiv_id = sys.argv[1] if len(sys.argv) > 1 else "2208.12396"
version = sys.argv[2] if len(sys.argv) > 2 else "v1"

versioned_id = f"{arxiv_id}{version}"
parts = arxiv_id.split('.')
year_month = parts[0]
paper_num = parts[1]

# Test source URL
source_url = f"https://arxiv.org/src/{year_month}/{paper_num}/{versioned_id}.tar.gz"
print(f"Testing source URL: {source_url}")

try:
    resp = requests.head(source_url, timeout=10, allow_redirects=True)
    print(f"Status Code: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
    print(f"Content-Length: {resp.headers.get('Content-Length', 'N/A')}")
    
    if resp.status_code == 200:
        print("✓ Source files are available!")
    elif resp.status_code == 404:
        print("✗ Source files NOT available (404)")
        print("\nTrying alternative formats...")
        
        # Try without version in path
        alt_url1 = f"https://arxiv.org/src/{year_month}/{paper_num}/{arxiv_id}.tar.gz"
        print(f"\nAlternative 1: {alt_url1}")
        resp1 = requests.head(alt_url1, timeout=10)
        print(f"  Status: {resp1.status_code}")
        
        # Try with different format
        alt_url2 = f"https://arxiv.org/e-print/{arxiv_id}"
        print(f"\nAlternative 2: {alt_url2}")
        resp2 = requests.head(alt_url2, timeout=10, allow_redirects=True)
        print(f"  Status: {resp2.status_code}")
        print(f"  Content-Type: {resp2.headers.get('Content-Type', 'N/A')}")
        print(f"  Content-Disposition: {resp2.headers.get('Content-Disposition', 'N/A')}")
        
        # Try GET to see actual content
        print(f"\n  Testing GET request...")
        resp2_get = requests.get(alt_url2, timeout=10, stream=True)
        print(f"  GET Status: {resp2_get.status_code}")
        print(f"  GET Content-Type: {resp2_get.headers.get('Content-Type', 'N/A')}")
        print(f"  GET Content-Length: {resp2_get.headers.get('Content-Length', 'N/A')}")
        
        # Check first few bytes
        if resp2_get.status_code == 200:
            chunk = next(resp2_get.iter_content(chunk_size=10))
            print(f"  First bytes: {chunk[:10]}")
            if chunk.startswith(b'\x1f\x8b'):  # gzip magic number
                print("  ✓ This is a gzip/tar.gz file!")
            else:
                print(f"  ⚠ Unknown format (starts with: {chunk[:10]})")
    else:
        print(f"✗ Unexpected status: {resp.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

