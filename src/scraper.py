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

    def _to_indian_url(self, url, query=""):
        """Convert global e-commerce URLs to Indian equivalents."""
        if not url:
            return url
        # Amazon: .com -> .in
        if 'amazon.com/' in url:
            url = url.replace('amazon.com/', 'amazon.in/')
        # If it's a global amazon link without country, redirect to amazon.in search
        if 'amazon.' in url and '.in' not in url and 'amazon.in' not in url:
            query_encoded = urllib.parse.quote_plus(query) if query else ""
            return f"https://www.amazon.in/s?k={query_encoded}"
        return url

    def scraper_backend_search(self, image_path, api_key):
        """
        Visual-First Search Strategy:
        1. Google Lens: Prioritize matches found DIRECTLY from the image.
        2. Filtering: Extract results from trusted Indian e-commerce sites.
        3. Fallback: Only use Google Shopping (text-based) if Lens doesn't have enough matches.
        """
        results = []
        trusted_vendors = ['amazon', 'flipkart', 'myntra', 'meesho', 'snapdeal']
        
        try:
            # Stage 1: Identification & Direct Visual Matching
            print(f"[INFO] Running Visual-First analysis via Google Lens...")
            public_url = self._upload_temp_image(image_path)
            if not public_url:
                raise Exception("Image host unavailable.")
                
            lens_params = {
                "engine": "google_lens",
                "url": public_url,
                "api_key": api_key,
                "gl": "in"
            }
            lens_resp = requests.get("https://serpapi.com/search", params=lens_params, timeout=30)
            lens_data = lens_resp.json()
            
            # Identify the product for potential fallback
            search_query = "Product"
            if "knowledge_graph" in lens_data and len(lens_data["knowledge_graph"]) > 0:
                search_query = lens_data["knowledge_graph"][0].get("title", "Product")
            elif "visual_matches" in lens_data and len(lens_data["visual_matches"]) > 0:
                search_query = lens_data["visual_matches"][0].get("title", "Product")
            
            # Step A: Extract Direct Shopping Matches from Lens Results
            if "visual_matches" in lens_data:
                for match in lens_data["visual_matches"]:
                    vendor_raw = match.get("source", "Store")
                    vendor_lower = vendor_raw.lower()
                    
                    # Filter for Trusted Indian Vendors
                    is_trusted = False
                    for trusted in trusted_vendors:
                        if trusted in vendor_lower:
                            is_trusted = True
                            vendor_raw = trusted.capitalize()
                            break
                    
                    if not is_trusted: continue
                    
                    # Convert URLs to Indian versions early
                    item_url = self._to_indian_url(match.get("link", ""), search_query)
                    
                    # Clean Price
                    price_val = 0
                    if "price" in match:
                        try:
                            # Try structured price first
                            p_str = match["price"].get("extracted_value")
                            currency = match["price"].get("currency", "₹")
                            
                            if not p_str:
                                # Fallback to parsing from current_price string
                                p_str = ''.join(filter(lambda x: x.isdigit() or x=='.', match["price"].get("current_price", "0")))
                                
                            p = float(p_str)
                            if (currency == "$" or currency == "USD") and p < 200:
                                p = p * 83.0  # USD to INR
                            elif currency == "£":
                                p = p * 105.0  # GBP to INR
                            elif p > 0 and p < 100:
                                p = p * 83.0  # Likely USD if very low
                            price_val = int(p)
                        except: pass
                    
                    # Final fallback: if vendor is trusted but price is still 0, 
                    # try extracting from snippet or just assign a dummy value 
                    # to keep the Visual Match alive (better than generic search)
                    if price_val <= 0:
                        import re
                        snippet = match.get("title", "") + " " + vendor_raw
                        nums = re.findall(r'₹\s?(\d+[,.]?\d*)', snippet)
                        if nums:
                            try: price_val = int(nums[0].replace(',', ''))
                            except: pass
                    
                    # If still 0, we still keep it if it's a direct visual hit
                    # We'll just show it at the bottom of the list
                    
                    results.append({
                        'vendor': vendor_raw,
                        'product_name': match.get("title", search_query)[:60] + "...",
                        'price': price_val,
                        'url': item_url,
                        'thumbnail': match.get("thumbnail", "")
                    })
                    if len(results) >= 8: break

            print(f"[INFO] Lens found {len(results)} visual matches.")

            # Stage 2: Google Shopping Fallback (Only if direct hits are VERY low)
            if len(results) < 2:
                print(f"[INFO] Low visual results. Triggering Google Shopping fallback for '{search_query}'...")
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
                    for item in shop_data["shopping_results"]:
                        if len(results) >= 12: break
                        url = item.get("link", "")
                        if any(r['url'] == url for r in results): continue
                        
                        vendor_raw = item.get("source", "Store")
                        price_str = item.get("price", "₹0")
                        try:
                            extracted_price = int(''.join(filter(str.isdigit, price_str.split('.')[0])))
                        except: extracted_price = 0
                        
                        # Skip zero-price results
                        if extracted_price <= 0:
                            continue
                        
                        # Convert URLs to Indian versions
                        item_url = self._to_indian_url(url, search_query)
                            
                        results.append({
                            'vendor': vendor_raw,
                            'product_name': item.get("title", search_query)[:60] + "...",
                            'price': extracted_price,
                            'url': item_url,
                            'thumbnail': item.get("thumbnail", "")
                        })

            if results:
                # Remove duplicates and sort by price (lowest first)
                results.sort(key=lambda x: x['price'])
        except Exception as e:
            print(f"[ERROR] Visual search failed: {e}")
            
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
            'Amazon': (-150, 200),
            'Flipkart': (-200, 150),
            'Myntra': (0, 400),
            'Meesho': (-400, -100),
            'Snapdeal': (-300, 100)
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
