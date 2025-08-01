#!/usr/bin/env python3
"""
Load .env and run scraper to fetch 100 posts
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env file
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    print("Loading .env file...")
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
                    print(f"Loaded {key}")

# Load credentials from file if GOOGLE_CREDS_FILE is set
if 'GOOGLE_CREDS_FILE' in os.environ:
    creds_path = Path(__file__).parent.parent / os.environ['GOOGLE_CREDS_FILE']
    if creds_path.exists():
        print(f"Loading Google credentials from {creds_path}...")
        with open(creds_path) as f:
            os.environ['GOOGLE_SHEETS_CREDS'] = f.read()
        print("Google credentials loaded!")

# Now import and run the scraper
try:
    from scraper_env import SavingsGuruScraperEnv
    
    print("\nRunning scraper to fetch latest posts...")
    scraper = SavingsGuruScraperEnv()
    
    # Update sheet from RSS (this will process up to 100 posts)
    scraper.update_sheet_from_rss()
    
    # Generate deals.json with all approved deals
    deals = scraper.generate_deals_json('../public/deals.json')
    
    print(f"\nSuccess! Generated deals.json with {len(deals)} deals")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()