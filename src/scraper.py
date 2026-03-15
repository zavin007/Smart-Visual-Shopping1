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
        2-Stage Real-Time Search:
        1. Google Lens: Identify the EXACT product name/model.
        2. Google Shopping: Fetch LIVE prices from Amazon, Flipkart, Myntra, etc. (India location).
        """
        results = []
        try:
            # Stage 1: Identification via Google Lens
            print(f"[INFO] Identifying product via Google Lens...")
            public_url = self._upload_temp_image(image_path)
            if not public_url:
                raise Exception("Image host (Catbox) is temporarily unavailable.")
                
            lens_params = {
                "engine": "google_lens",
                "url": public_url,
                "api_key": api_key
            }
            lens_resp = requests.get("https://serpapi.com/search", params=lens_params, timeout=30)
            lens_data = lens_resp.json()
            
            # Extract the most accurate title
            search_query = "Product"
            if "knowledge_graph" in lens_data and len(lens_data["knowledge_graph"]) > 0:
                search_query = lens_data["knowledge_graph"][0].get("title", "Product")
            elif "visual_matches" in lens_data and len(lens_data["visual_matches"]) > 0:
                search_query = lens_data["visual_matches"][0].get("title", "Product")
            
            print(f"[INFO] Product identified as: '{search_query}'")
            
            # Stage 2: Real-time Price Fetching via Google Shopping (India)
            print(f"[INFO] Fetching LIVE Indian prices for '{search_query}'...")
            shopping_params = {
                "engine": "google_shopping",
                "q": search_query,
                "location": "India",
                "gl": "in",
                "hl": "en",
                "api_key": api_key
            }
            shop_resp = requests.get("https://serpapi.com/search", params=shopping_params, timeout=30)
            shop_data = shop_resp.json()
            
            if "shopping_results" in shop_data:
                for item in shop_data["shopping_results"][:10]:
                    vendor_raw = item.get("source", "Store")
                    price_str = item.get("price", "₹0")
                    # Clean price string (e.g., "₹1,299.00" -> 1299)
                    try:
                        extracted_price = int(''.join(filter(str.isdigit, price_str.split('.')[0])))
                    except:
                        extracted_price = 0
                        
                    results.append({
                        'vendor': vendor_raw,
                        'product_name': item.get("title", search_query)[:60] + "...",
                        'price': extracted_price,
                        'url': item.get("link", ""),
                        'thumbnail': item.get("thumbnail", "")
                    })
            
            # Fallback: If no shopping results, try visual matches from Stage 1
            if not results and "visual_matches" in lens_data:
                print(f"[INFO] No direct shopping results. Using top visual matches...")
                for match in lens_data["visual_matches"][:5]:
                    results.append({
                        'vendor': match.get("source", "Web Store"),
                        'product_name': match.get("title", search_query)[:60] + "...",
                        'price': 0, # Mark as 0 if unknown
                        'url': match.get("link", ""),
                        'thumbnail': match.get("thumbnail", "")
                    })

            if results:
                print(f"[OK] Found {len(results)} verifiable results!")
                # Remove results with 0 price if possible, or sort them last
                results.sort(key=lambda x: (x['price'] == 0, x['price']))
        except Exception as e:
            print(f"[ERROR] Live search failed: {e}")
            
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
