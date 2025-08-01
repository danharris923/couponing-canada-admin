#!/usr/bin/env python3
"""
Simple script to run scraper using .env file
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path to find .env
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to load .env file
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    print("Loading .env file...")
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Load credentials from file if specified
if 'GOOGLE_CREDS_FILE' in os.environ and not os.environ.get('GOOGLE_SHEETS_CREDS'):
    creds_path = Path(__file__).parent.parent / os.environ['GOOGLE_CREDS_FILE']
    if creds_path.exists():
        with open(creds_path) as f:
            os.environ['GOOGLE_SHEETS_CREDS'] = f.read()
        print(f"Loaded credentials from {os.environ['GOOGLE_CREDS_FILE']}")

# Import and run scraper
from scraper_env import SavingsGuruScraperEnv

def main():
    print("\nRunning SavingsGuru Scraper")
    print(f"Spreadsheet ID: {os.environ.get('SPREADSHEET_ID')}")
    
    try:
        scraper = SavingsGuruScraperEnv()
        
        # Run scraper to fetch new deals
        print("\nFetching deals from RSS feed...")
        scraper.update_sheet_from_rss()
        
        print("\nDone! Check your Google Sheet")
        print("Next: Review deals and change Status to 'approved'")
        
        # Ask if user wants to generate deals.json
        response = input("\nGenerate deals.json from approved deals? (y/n): ")
        if response.lower() == 'y':
            scraper.generate_deals_json()
            print("Generated public/deals.json")
            
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()