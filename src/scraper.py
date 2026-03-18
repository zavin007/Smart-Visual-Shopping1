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
        """
        Search-safe conversion of global URLs to Indian equivalents.
        """
        if not url: return url
        
        url_lower = url.lower()
        search_q = query or "Product"
        query_encoded = urllib.parse.quote_plus(search_q)
        
        # 1. If it's already a trusted Indian domain, use it directly (Live links)
        indian_patterns = {
            'amazon.in': 'Amazon',
            'flipkart.com': 'Flipkart',
            'myntra.com': 'Myntra',
            'meesho.com': 'Meesho',
            'snapdeal.com': 'Snapdeal',
            'ajio.com': 'Ajio'
        }
        
        for pattern, vendor in indian_patterns.items():
            if pattern in url_lower:
                if vendor == 'Amazon' and 'tag=' in url:
                    url = url.split('tag=')[0].rstrip('?&')
                return url
            
        # 2. For Global hits, redirect to the most relevant Indian search page
        if 'amazon.' in url_lower:
            return f"https://www.amazon.in/s?k={query_encoded}"
        elif 'flipkart.' in url_lower:
            return f"https://www.flipkart.com/search?q={query_encoded}"
        elif 'myntra.' in url_lower:
            return f"https://www.myntra.com/{search_q.lower().replace(' ', '-')}"
            
        # 3. Default fallback: use Amazon.in search
        return f"https://www.amazon.in/s?k={query_encoded}"

    def scraper_backend_search(self, image_path, api_key):
        """
        Visual-First Search Strategy with High Accuracy Priority.
        Ensures Google Lens visual matches are the primary source of results.
        """
        results = []
        main_platforms = ['Amazon', 'Flipkart', 'Myntra', 'Meesho', 'Snapdeal']
        processed_platforms = set()
        
        try:
            # Stage 1: Identification & Direct Visual Matching (CRITICAL)
            print(f"[INFO] Running Visual-First analysis via Google Lens...")
            public_url = self._upload_temp_image(image_path)
            if not public_url:
                raise Exception("Image host unavailable.")
                
            lens_params = {"engine": "google_lens", "url": public_url, "api_key": api_key, "gl": "in"}
            lens_resp = requests.get("https://serpapi.com/search", params=lens_params, timeout=30)
            lens_data = lens_resp.json()
            
            # The most accurate product identity discovered by AI
            search_query = "Product"
            if "knowledge_graph" in lens_data and lens_data["knowledge_graph"]:
                search_query = lens_data["knowledge_graph"][0].get("title", "Product")
            elif "visual_matches" in lens_data and lens_data["visual_matches"]:
                search_query = lens_data["visual_matches"][0].get("title", "Product")
            
            # Step A: Prioritize Exact Visual Matches from Lens
            if "visual_matches" in lens_data:
                for match in lens_data["visual_matches"]:
                    vendor_raw = match.get("source", "Store")
                    vendor_lower = vendor_raw.lower()
                    
                    # Track which platforms we have direct visual matches for
                    matched_vendor = None
                    for p in main_platforms:
                        if p.lower() in vendor_lower:
                            matched_vendor = p
                            break
                    
                    display_title = match.get("title", search_query)
                    item_url = self._to_indian_url(match.get("link", ""), display_title)
                    
                    # Extract Price with high-aggression fetching
                    price_val = 0
                    if "price" in match:
                        try:
                            p_str = match["price"].get("extracted_value") or ''.join(filter(lambda x: x.isdigit() or x=='.', match["price"].get("current_price", "0")))
                            p = float(p_str)
                            currency = match["price"].get("currency", "₹")
                            if currency in ["$", "USD"]: p *= 83.0
                            elif currency == "£": p *= 105.0
                            price_val = int(p)
                        except: pass
                    
                    # Regex fallback for price
                    is_estimated = False
                    if price_val <= 0:
                        import re
                        raw_text = f"{match.get('title', '')} {match.get('source', '')} {match.get('link', '')}"
                        regex_hits = re.findall(r'(?:₹|Rs\.?|INR)\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)', raw_text)
                        if regex_hits:
                            try: price_val = int(float(regex_hits[0].replace(',', '')))
                            except: pass
                    
                    if price_val <= 0:
                        price_val = self._estimate_price(0, matched_vendor or "Amazon", display_title)
                        is_estimated = True
                    
                    results.append({
                        'vendor': matched_vendor or vendor_raw,
                        'product_name': display_title[:60] + "...",
                        'price': price_val,
                        'is_estimated': is_estimated,
                        'url': item_url,
                        'thumbnail': match.get("thumbnail", ""),
                        'is_visual_match': True # Mark as high-accuracy result
                    })
                    if matched_vendor: processed_platforms.add(matched_vendor)
                    if len(results) >= 5: break

            # Stage 2: Smart Completion (Only for missing main platforms)
            # We use the EXACT identity found above to fill in the gaps accurately
            base_price = self._get_base_price(search_query)
            for platform in main_platforms:
                if platform not in processed_platforms:
                    results.append({
                        'vendor': platform,
                        'product_name': f"Live match search: {search_query}",
                        'price': self._estimate_price(base_price, platform, search_query),
                        'is_estimated': True,
                        'url': self._generate_url(platform, search_query),
                        'thumbnail': "",
                        'is_visual_match': False
                    })

            # Stage 3: Ranking - Visual matches ALWAYS come first
            results.sort(key=lambda x: (not x['is_visual_match'], x['price']))
            return results
                
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            
        return results

    def _generate_url(self, platform, query):
        """Generate search URL for platform"""
        base_url = self.platforms.get(platform, '')
        if platform == 'Myntra':
            return f"{base_url}{query.lower().replace(' ', '-')}"
        return f"{base_url}{urllib.parse.quote_plus(query)}"
    
    def _get_base_price(self, query):
        """Estimate a realistic base price based on item category."""
        q = query.lower()
        if any(x in q for x in ['laptop', 'macbook', 'pc']): return random.randint(35000, 95000)
        if any(x in q for x in ['smartphone', 'iphone', 'mobile']): return random.randint(15000, 85000)
        if any(x in q for x in ['speaker', 'bluetooth speaker']): return random.randint(3500, 25000)
        if any(x in q for x in ['headphone', 'earbuds', 'airpods']): return random.randint(1500, 18000)
        if any(x in q for x in ['nike', 'adidas', 'shoe', 'sneaker']): return random.randint(1800, 4500)
        if 'watch' in q: return random.randint(1200, 5000)
        if 'kurta' in q or 'shirt' in q: return random.randint(600, 1800)
        if 'bag' in q or 'backpack' in q: return random.randint(900, 3000)
        return random.randint(500, 3000)

    def _estimate_price(self, base_price, platform, query="Product"):
        if base_price <= 0: base_price = self._get_base_price(query)
        variance = {'Amazon': (-150, 200), 'Flipkart': (-200, 150), 'Myntra': (0, 400), 'Meesho': (-400, -100), 'Snapdeal': (-300, 100)}
        low, high = variance.get(platform, (-100, 100))
        return max(399, base_price + random.randint(low, high))
    
    def search_all(self, query):
        """Text-based simulated fallback"""
        results = []
        base_price = self._get_base_price(query)
        for platform in self.platforms.keys():
            results.append({
                'vendor': platform,
                'product_name': f"{query} on {platform}",
                'price': self._estimate_price(base_price, platform, query),
                'url': self._generate_url(platform, query),
                'is_visual_match': False
            })
        results.sort(key=lambda x: x['price'])
        return results

if __name__ == "__main__":
    scraper = WebScraper()
    print(scraper.search_all("Nike Shoes"))
