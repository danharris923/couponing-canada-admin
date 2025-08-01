#!/usr/bin/env python3
"""
Updated scraper that works with environment variables instead of files
"""

import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import feedparser
import requests
import re
from urllib.parse import urlparse, parse_qs
import time
import tempfile

class SavingsGuruScraperEnv:
    def __init__(self):
        # Get credentials from environment variable
        creds_json = os.environ.get('GOOGLE_SHEETS_CREDS')
        spreadsheet_id = os.environ.get('SPREADSHEET_ID')
        
        if not creds_json:
            raise ValueError("GOOGLE_SHEETS_CREDS environment variable not set")
        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID environment variable not set")
        
        # Parse JSON credentials from environment variable
        creds_data = json.loads(creds_json)
        
        # Create temporary file for credentials (required by oauth2client)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(creds_data, f)
            temp_creds_file = f.name
        
        try:
            # Google Sheets setup
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(temp_creds_file, scope)
            self.client = gspread.authorize(creds)
            
            # Open spreadsheet
            self.sheet = self.client.open_by_key(spreadsheet_id).sheet1
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_creds_file):
                os.unlink(temp_creds_file)
        
        # Amazon affiliate tag - correct tracking tag
        self.affiliate_tag = "savingsgurucc-20"
    
    def clean_description(self, raw_description, product_title="", amazon_url=None):
        """Create SEO-friendly descriptions using real Amazon product descriptions"""
        # If we have an Amazon URL, try to get real product description
        if amazon_url and "/dp/" in amazon_url:
            amazon_desc = self.scrape_amazon_description(amazon_url)
            if amazon_desc:
                print(f"Using Amazon description: {amazon_desc[:50]}...")
                return amazon_desc
        
        # Fallback: Clean RSS description if available
        if raw_description:
            # Remove HTML tags and decode entities
            import html
            from bs4 import BeautifulSoup
            
            cleaned = html.unescape(raw_description)
            soup = BeautifulSoup(cleaned, 'html.parser')
            text = soup.get_text()
            
            # Remove unwanted phrases and artifacts
            unwanted_phrases = [
                "sells on Amazon. I think the price is very good.",
                "Please read some of the reviews and see people thought of the product.",
                "**If you're not sure whether to buy, add to cart, and you can come back to it later!**",
                "The post", "appeared first on", "Savings Guru", "SavingsGuru",
                "[…]", "&#8230;", "[read more]", "Continue reading",
                "savingsguru.ca"
            ]
            
            for phrase in unwanted_phrases:
                text = text.replace(phrase, "")
            
            # Clean up extra whitespace and newlines
            text = re.sub(r'\s+', ' ', text).strip()
            
            # If we have decent cleaned text, use it
            if text and len(text) > 20:
                return text[:150] + "..." if len(text) > 150 else text
        
        # Final fallback: Generate SEO description
        return self.generate_seo_description(product_title)
    
    def generate_seo_description(self, product_title=""):
        """Generate engaging, SEO-friendly descriptions using a variety of generic templates"""
        import random
        
        # Large collection of snappy, SEO-friendly descriptions
        templates = [
            "🔥 DEAL ALERT! Incredible savings on this must-have item. Premium quality meets unbeatable value - don't miss out!",
            "⚡ HOT DEAL! Get more bang for your buck with this amazing offer. Quality you can trust at a price you'll love!",
            "🎯 This deal is too good to pass up! Discover why thousands are raving about this incredible value. Act fast!",
            "💫 Your new favorite find! This amazing product combines style, quality, and savings in one perfect package.",
            "🚀 Level up your life with this game-changing deal! Don't let this opportunity slip away - grab yours today!",
            "⭐ Customer favorite alert! Join the thousands who've already discovered this incredible value. Limited time only!",
            "🏆 WINNER! This top-rated product delivers exceptional quality at an unbeatable price. Your wallet will thank you!",
            "💎 Hidden gem discovered! Premium features at a fraction of the cost. Smart shoppers are loving this deal!",
            "🎊 Celebrate these savings! This fantastic offer won't last long. Treat yourself to quality for less!",
            "🌟 5-star quality, amazing price! See why this product is flying off the shelves. Limited quantity available!",
            "💰 Money-saving magic! Get premium quality without the premium price tag. This deal is pure gold!",
            "🔓 Unlock incredible savings! This exclusive offer gives you more value for your money. Don't wait!",
            "🎁 Gift yourself this amazing deal! Perfect for treating yourself or someone special. Quality guaranteed!",
            "⏰ Time-sensitive offer! Smart shoppers know a good deal when they see one. This won't last long!",
            "🌈 Brighten your day with amazing savings! This fantastic product delivers quality and value in one package.",
            "🏅 Award-winning value! Customers love this product for good reason. Join the satisfied buyers today!",
            "🔥 Trending now! This hot item is flying off the shelves. Secure yours at this incredible price!",
            "💡 Smart choice alert! This brilliant buy offers exceptional value for money. Your future self will thank you!",
            "🎪 Spectacular savings! Step right up to this amazing deal. Quality performance at an unbeatable price!",
            "🌺 Blooming with value! This delightful deal brings quality and savings together beautifully.",
            "⚖️ Perfect balance of quality and price! This smart buy delivers everything you want at a price you'll love.",
            "🎵 Music to your wallet! This harmonious blend of quality and value creates the perfect deal symphony.",
            "🏖️ Summer savings vibes! Cool deals, hot prices, and quality that shines. Dive into these savings!",
            "🍀 Lucky you! This rare find offers premium quality at an incredibly lucky price. Fortune favors the bold!",
            "🎭 Drama-free shopping! This straightforward deal delivers exactly what you want at a great price.",
            "🚗 Fast-track to savings! This express deal gets you premium quality without the premium wait or price!",
            "🍯 Sweet deal alert! This golden opportunity offers pure value that's as satisfying as honey.",
            "🌙 Dreamy prices, quality reality! This night-and-day difference in value will have you sleeping soundly.",
            "🎨 Masterpiece pricing! This artfully crafted deal paints the perfect picture of value and quality.",
            "🏰 Royal treatment, peasant prices! Feel like royalty with this premium quality at a commoner's cost!"
        ]
        
        return random.choice(templates)
        
    def parse_rss_feed(self, feed_url="https://www.savingsguru.ca/feed/"):
        """Parse RSS feed from SavingsGuru.ca"""
        feed = feedparser.parse(feed_url)
        deals = []
        
        for entry in feed.entries[:100]:  # Get latest 100 entries
            # We'll get the Amazon URL during processing, so just store raw description for now
            deal = {
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'raw_description': entry.get('summary', ''),  # Store raw for later processing
                'status': 'approved'  # Auto-approved since already vetted on original site
            }
            deals.append(deal)
            
        return deals
    
    def extract_amazon_link(self, deal_url):
        """Extract real Amazon product link from SavingsGuru post"""
        try:
            from bs4 import BeautifulSoup
            
            response = requests.get(deal_url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for amzn.to short links (these are the real product links)
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'amzn.to/' in href:
                    # Follow redirect to get actual Amazon URL
                    redirect_response = requests.head(href, allow_redirects=True, timeout=10)
                    final_url = redirect_response.url
                    
                    # Add our affiliate tag
                    return self.add_affiliate_tag(final_url)
            
            # Fallback: look for direct Amazon product URLs
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'amazon' in href.lower() and ('/dp/' in href or '/gp/product/' in href):
                    return self.add_affiliate_tag(href)
                    
            return None
            
        except Exception as e:
            print(f"Error extracting Amazon link: {e}")
            return None
    
    def add_affiliate_tag(self, amazon_url):
        """Add affiliate tag to Amazon URL"""
        parsed = urlparse(amazon_url)
        params = parse_qs(parsed.query)
        params['tag'] = [self.affiliate_tag]
        
        # Rebuild URL with affiliate tag
        new_query = '&'.join([f"{k}={v[0]}" for k, v in params.items()])
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
    
    def extract_product_image(self, deal_url):
        """Extract the main product image from SavingsGuru post"""
        try:
            from bs4 import BeautifulSoup
            
            response = requests.get(deal_url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the main product image - usually the first content image
            content_img = soup.select_one('.entry-content img, .post-content img, article img')
            if content_img and content_img.get('src'):
                img_url = content_img.get('src')
                # Make sure it's a full URL
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://www.savingsguru.ca' + img_url
                return img_url
            
            # Fallback: look for featured image
            featured_img = soup.select_one('img.wp-post-image, img.attachment-full')
            if featured_img and featured_img.get('src'):
                img_url = featured_img.get('src')
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://www.savingsguru.ca' + img_url
                return img_url
            
            return None
            
        except Exception as e:
            print(f"Error extracting product image: {e}")
            return None
    
    def extract_price_info(self, description):
        """Extract price information from description"""
        # Try multiple price patterns
        price_pattern = r'\$([\d,]+(?:\.\d{2})?)'  # Support commas in prices
        prices = re.findall(price_pattern, description)
        
        if len(prices) >= 2:
            current_price = float(prices[0].replace(',', ''))
            original_price = float(prices[1].replace(',', ''))
        elif len(prices) == 1:
            current_price = float(prices[0].replace(',', ''))
            # Estimate original price with 30% markup
            original_price = current_price * 1.3
        else:
            # Fallback: Generate realistic prices based on product category
            import random
            title_lower = description.lower()
            
            if any(word in title_lower for word in ['electronics', 'tech', 'phone', 'laptop', 'tv']):
                current_price = random.uniform(199, 899)
                original_price = current_price * random.uniform(1.3, 1.6)
            elif any(word in title_lower for word in ['clothing', 'shirt', 'pants', 'dress', 'shoes', 'tank', 'cardigan', 'leggings']):
                current_price = random.uniform(19, 79)
                original_price = current_price * random.uniform(1.2, 1.5)
            elif any(word in title_lower for word in ['home', 'kitchen', 'furniture', 'decor', 'mattress', 'rack', 'storage', 'basket']):
                current_price = random.uniform(29, 199)
                original_price = current_price * random.uniform(1.3, 1.7)
            elif any(word in title_lower for word in ['food', 'snack', 'cake', 'cookie', 'oreo', 'pretzel']):
                current_price = random.uniform(3, 15)
                original_price = current_price * random.uniform(1.2, 1.4)
            else:
                # Generic fallback
                current_price = random.uniform(24, 89)
                original_price = current_price * random.uniform(1.3, 1.6)
        
        # Calculate discount percentage
        if original_price > current_price:
            discount = int(((original_price - current_price) / original_price) * 100)
        else:
            discount = 25  # Default discount
            
        return round(current_price, 2), round(original_price, 2), discount
    
    def scrape_amazon_description(self, amazon_url):
        """Scrape product description from Amazon for SEO gold"""
        try:
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-CA,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            
            response = requests.get(amazon_url, headers=headers, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract title and basic info for products without feature bullets
            title_elem = soup.select_one('#productTitle')
            product_title = title_elem.get_text().strip() if title_elem else ""
            
            # Try multiple description selectors in order of preference
            description_approaches = [
                # Approach 1: Feature bullets with colons (detailed descriptions)
                {
                    'selectors': ['#feature-bullets ul li span.a-list-item', '[data-feature-name="featurebullets"] ul li span'],
                    'requires_colon': True,
                    'min_length': 20
                },
                # Approach 2: Product description paragraphs
                {
                    'selectors': ['#productDescription p', '#aplus_feature_div p'],
                    'requires_colon': False,
                    'min_length': 30
                },
                # Approach 3: Any feature bullets (less strict)
                {
                    'selectors': ['#feature-bullets .a-list-item', '.a-unordered-list.a-nostyle.a-vertical li span'],
                    'requires_colon': False,
                    'min_length': 15
                }
            ]
            
            for approach in description_approaches:
                for selector in approach['selectors']:
                    elements = soup.select(selector)
                    if elements:
                        descriptions = []
                        for elem in elements[:3]:  # Take first 3 elements
                            text = elem.get_text().strip()
                            text = ' '.join(text.split())  # Clean whitespace
                            
                            skip_phrases = ['make sure', 'please note', 'important', 'clothing, shoes & accessories', 
                                          'home & kitchen', 'sports & outdoors', 'health & personal care',
                                          'date first available', 'best sellers rank', 'customer reviews']
                            
                            colon_check = ':' in text if approach['requires_colon'] else True
                            
                            if (text and len(text) > approach['min_length'] and len(text) < 300 and 
                                not any(skip in text.lower() for skip in skip_phrases) and
                                colon_check and not text.startswith('•') and not text.startswith('-')):
                                descriptions.append(text)
                        
                        if descriptions:
                            # Join descriptions, limit to ~150 chars for cards
                            combined = '. '.join(descriptions)
                            if len(combined) > 150:
                                combined = combined[:147] + "..."
                            print(f"Extracted Amazon description: {combined[:50]}...")
                            return combined
            
            # Fallback: Use product title with a generic description if we can't find anything
            if product_title and len(product_title) > 10:
                fallback = f"{product_title[:100]}... - High quality product with great value"
                if len(fallback) > 150:
                    fallback = fallback[:147] + "..."
                print(f"Using title fallback: {fallback[:50]}...")
                return fallback
            
            return None
            
        except Exception as e:
            print(f"Error scraping Amazon description: {e}")
            return None
    
    def scrape_amazon_discount(self, amazon_url):
        """Scrape discount percentage from Amazon product page for sale tags"""
        try:
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-CA,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            
            response = requests.get(amazon_url, headers=headers, timeout=15)
            if response.status_code != 200:
                return 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for discount percentage - same as your savingsPercentage extraction
            discount_selectors = [
                '.savingsPercentage',
                '.a-text-strike + .a-text-price .a-offscreen',
                '[data-a-color="price"] .a-text-strike + .a-text-price',
                '.a-price-savings-percentage',
            ]
            
            for selector in discount_selectors:
                discount_elem = soup.select_one(selector)
                if discount_elem:
                    discount_text = discount_elem.get_text().strip()
                    print(f"Found discount text: '{discount_text}' from selector: {selector}")
                    # Extract percentage number (handle negative signs like "-7%")
                    discount_match = re.search(r'-?(\d+)%', discount_text)
                    if discount_match:
                        percentage = int(discount_match.group(1))
                        print(f"Extracted discount percentage: {percentage}%")
                        return percentage
            
            return 0
            
        except Exception as e:
            print(f"Error scraping Amazon discount: {e}")
            return 0
    
    def scrape_amazon_price(self, amazon_url):
        """Scrape current and original price from Amazon"""
        try:
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-CA,en;q=0.9',
            }
            
            response = requests.get(amazon_url, headers=headers, timeout=15)
            if response.status_code != 200:
                return 0, 0, 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract current price
            current_price = 0
            price_selectors = ['.a-price-whole', '.a-price .a-offscreen']
            
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text().strip()
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace('$', '').replace(',', ''))
                    if price_match:
                        current_price = float(price_match.group())
                        break
            
            # Extract original price
            original_price = 0
            original_selectors = ['.a-text-strike .a-offscreen', '#priceblock_listprice']
            
            for selector in original_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text().strip()
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace('$', '').replace(',', ''))
                    if price_match:
                        original_price = float(price_match.group())
                        break
            
            return current_price, original_price, 0
            
        except Exception as e:
            print(f"Error scraping Amazon price: {e}")
            return 0, 0, 0
    
    def update_sheet_from_rss(self):
        """Fetch RSS and update Google Sheet"""
        print("Fetching RSS feed...")
        deals = self.parse_rss_feed()
        
        # Check if sheet has headers, if not add them
        try:
            headers = self.sheet.row_values(1)
            if not headers:
                self.setup_headers()
        except:
            self.setup_headers()
        
        # Get existing IDs to avoid duplicates
        try:
            existing_ids = self.sheet.col_values(1)[1:]  # Skip header
        except:
            existing_ids = []
        
        new_deals = []
        for deal in deals:
            # Create unique ID from title
            deal_id = re.sub(r'[^a-zA-Z0-9]', '', deal['title'].lower())[:20]
            
            if deal_id not in existing_ids:
                print(f"Processing: {deal['title'][:50]}...")
                
                # Extract Amazon link and product image
                amazon_url = self.extract_amazon_link(deal['link'])
                product_image = self.extract_product_image(deal['link'])
                
                # Get real prices and discount from Amazon
                if amazon_url and "/dp/" in amazon_url:
                    # First get discount percentage (for red sale tags) 
                    discount = self.scrape_amazon_discount(amazon_url)
                    
                    # Then get actual prices (scraped but not always shown)
                    current_price, original_price, _ = self.scrape_amazon_price(amazon_url)
                    
                    # Use the scraped discount from Amazon's own percentage display
                    # This is more accurate than calculated discount
                else:
                    current_price = 0
                    original_price = 0
                    discount = 0
                
                # Get SEO-friendly description using Amazon URL (the SEO gold!)
                seo_description = self.clean_description(deal['raw_description'], deal['title'], amazon_url)
                
                # Prepare row data
                row_data = [
                    deal_id,
                    deal['title'],
                    deal['link'],
                    amazon_url or deal['link'],
                    current_price,
                    original_price,
                    discount,
                    product_image or '/placeholder-deal.svg',  # Use real product image from RSS post
                    seo_description,  # Real Amazon description - SEO gold!
                    'General',  # Category
                    'approved',  # Status - auto-approved
                    datetime.now().strftime('%Y-%m-%d'),
                    ''  # Notes
                ]
                
                new_deals.append(row_data)
        
        if new_deals:
            print(f"Adding {len(new_deals)} new deals to sheet...")
            # Find next empty row
            next_row = len(self.sheet.col_values(1)) + 1
            
            # Add all new deals
            for deal in new_deals:
                self.sheet.insert_row(deal, next_row)
                next_row += 1
                time.sleep(1)  # Rate limiting
            
            print(f"Successfully added {len(new_deals)} deals!")
        else:
            print("No new deals found.")
    
    def setup_headers(self):
        """Add headers to the sheet"""
        headers = [
            'ID', 'Title', 'Original URL', 'Amazon URL', 
            'Price', 'Original Price', 'Discount %', 'Image URL',
            'Description', 'Category', 'Status', 'Date Added', 'Notes'
        ]
        self.sheet.insert_row(headers, 1)
        print("Added headers to sheet")
    
    def generate_deals_json(self, output_path='../public/deals.json'):
        """Generate deals.json from approved deals in sheet"""
        print("Fetching approved deals from sheet...")
        
        # Get all data
        all_data = self.sheet.get_all_values()
        if len(all_data) <= 1:
            print("No data in sheet")
            return []
        
        headers = all_data[0]
        deals = []
        
        for row in all_data[1:]:  # Skip header
            if len(row) >= 11 and row[10] == 'approved':  # Status column
                try:
                    deal = {
                        'id': row[0],
                        'title': row[1],
                        'imageUrl': row[7] or '/placeholder-deal.svg',
                        'price': float(row[4]) if row[4] else 0,
                        'originalPrice': float(row[5]) if row[5] else 0,
                        'discountPercent': int(row[6]) if row[6] else 0,
                        'category': row[9],
                        'description': row[8],
                        'affiliateUrl': row[3],
                        'featured': 'featured' in row[12].lower() if len(row) > 12 else False,
                        'dateAdded': row[11]
                    }
                    deals.append(deal)
                except Exception as e:
                    print(f"Error processing row: {e}")
        
        # Sort by date, newest first
        deals.sort(key=lambda x: x['dateAdded'], reverse=True)
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(deals, f, indent=2)
        
        print(f"Generated deals.json with {len(deals)} approved deals")
        return deals


def main():
    """Test the scraper with environment variables"""
    print("Testing SavingsGuru Scraper with environment variables...")
    
    try:
        scraper = SavingsGuruScraperEnv()
        scraper.update_sheet_from_rss()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo run locally, set environment variables:")
        print("Windows PowerShell:")
        print('  $env:GOOGLE_SHEETS_CREDS = Get-Content credentials/google_service_account.json -Raw')
        print('  $env:SPREADSHEET_ID = "your-sheet-id"')
        print("\nLinux/Mac:")
        print('  export GOOGLE_SHEETS_CREDS=$(cat credentials/google_service_account.json)')
        print('  export SPREADSHEET_ID="your-sheet-id"')

if __name__ == "__main__":
    main()