"""
Web Scraper for E-commerce Price Comparison
Includes true Reverse Image Search via Google Lens (SerpApi).
"""
import urllib.parse
import random
import requests
import json
import os

class WebScraper:
    """
    Handles both simulated text-based scraping and true Google Lens reverse image search.
    """
    
    def __init__(self):
        self.platforms = {
            'Amazon': 'https://www.amazon.in/s?k=',
            'Flipkart': 'https://www.flipkart.com/search?q=',
            'Myntra': 'https://www.myntra.com/',
            'Meesho': 'https://www.meesho.com/search?q=',
            'Snapdeal': 'https://www.snapdeal.com/search?keyword='
        }
    
    def _upload_temp_image(self, file_path):
        """Upload image to anonymous temporary host (catbox.moe) for Google Lens public URL requirement."""
        try:
            url = "https://catbox.moe/user/api.php"
            data = {"reqtype": "fileupload"}
            with open(file_path, "rb") as f:
                files = {"fileToUpload": f}
                response = requests.post(url, data=data, files=files, timeout=15)
                response.raise_for_status()
                return response.text.strip()
        except Exception as e:
            print(f"[ERROR] Temp image upload failed: {e}")
            return None

    def scraper_backend_search(self, image_path, api_key):
        """
        True Reverse Image Search using Deep Web search engine.
        Mimics the native Google Lens experience by returning high-volume raw visual matches.
        """
        results = []
        try:
            # 1. Upload image to get public URL
            print(f"[INFO] Uploading image for Deep Web analysis...")
            public_url = self._upload_temp_image(image_path)
            
            if not public_url:
                raise Exception("Failed to get public image URL")
                
            print(f"[INFO] Sending to Deep Web Search API (Native Lens Mode)...")
            
            # 2. Call SerpApi Google Lens
            params = {
                "engine": "google_lens",
                "url": public_url,
                "api_key": api_key
            }
            
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            data = response.json()
            
            # 3. Parse RAW Visual Matches (High Volume)
            if "visual_matches" in data:
                matches = data["visual_matches"]
                
                for match in matches:
                    # Allow up to 24 results for a full "Google Lens" experience
                    if len(results) >= 24:
                        break
                        
                    if "price" in match:
                        vendor_raw = match.get("source", "Web Store")
                        
                        # Currency Formatting
                        currency = match["price"].get("currency", "")
                        price_str = match["price"].get("extracted_value", 0)
                        try:
                            price = float(price_str)
                            # Convert USD to INR 
                            if currency == "$" or price < 200:
                                price = price * 84.0 
                        except:
                            continue
                            
                        title = match.get("title", "Product Match")[:50] + "..."
                        
                        results.append({
                            'vendor': vendor_raw,
                            'product_name': title,
                            'price': int(price),
                            'url': match.get("link", ""),
                            'thumbnail': match.get("thumbnail", "")
                        })
            
            if results:
                # Sort by price
                results.sort(key=lambda x: x['price'])
                print(f"[OK] Google Lens returned {len(results)} exact visual matches!")
            else:
                print("[WARN] Google Lens found no priced items. Falling back...")
                
        except Exception as e:
            print(f"[ERROR] API failure: {e}")
            
        return results

    def _generate_url(self, platform, query):
        """Generate search URL for platform"""
        base_url = self.platforms.get(platform, '')
        
        if platform == 'Myntra':
            formatted_query = query.lower().replace(' ', '-')
            return f"{base_url}{formatted_query}"
        else:
            formatted_query = urllib.parse.quote_plus(query)
            return f"{base_url}{formatted_query}"
    
    def _estimate_price(self, base_price, platform):
        # ... existing generic price estimator
        variance = {
            'Amazon': (-200, 300),
            'Flipkart': (-300, 200),
            'Myntra': (0, 500),
            'Meesho': (-500, -100),
            'Snapdeal': (-400, 100)
        }
        
        low, high = variance.get(platform, (-100, 100))
        price = base_price + random.randint(low, high)
        return max(299, price)
    
    def search_all(self, query):
        """
        Text-based simulated fallback if Google Lens isn't used
        """
        results = []
        search_query = query.strip()
        query_lower = query.lower()
        
        if 'nike' in query_lower or 'adidas' in query_lower or 'puma' in query_lower:
            base_price = random.randint(2500, 5000)
        elif 'shoe' in query_lower or 'sneaker' in query_lower:
            base_price = random.randint(1500, 3500)
        elif 'watch' in query_lower:
            base_price = random.randint(1000, 4000)
        elif 'bag' in query_lower or 'backpack' in query_lower:
            base_price = random.randint(800, 2500)
        else:
            base_price = random.randint(500, 2000)
        
        for platform in self.platforms.keys():
            price = self._estimate_price(base_price, platform)
            url = self._generate_url(platform, search_query)
            
            results.append({
                'vendor': platform,
                'product_name': f"{search_query} on {platform}",
                'price': price,
                'url': url
            })
            
        results.sort(key=lambda x: x['price'])
        return results


# Test
if __name__ == "__main__":
    scraper = WebScraper()
    print("Testing with 'Nike Shoes'...")
    results = scraper.search_all("Nike Shoes")
    for r in results:
        print(f"{r['vendor']}: ₹{r['price']} - {r['url']}")
