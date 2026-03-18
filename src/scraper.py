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
        
        indian_patterns = {
            'amazon.in': 'Amazon',
            'flipkart.com': 'Flipkart',
            'myntra.com': 'Myntra',
            'meesho.com': 'Meesho',
            'snapdeal.com': 'Snapdeal'
        }
        
        for p, vendor in indian_patterns.items():
            if p in url_lower:
                if vendor == 'Amazon' and 'tag=' in url:
                    url = url.split('tag=')[0].rstrip('?&')
                return url
            
        if 'amazon.' in url_lower:
            return f"https://www.amazon.in/s?k={query_encoded}"
        elif 'flipkart.' in url_lower:
            return f"https://www.flipkart.com/search?q={query_encoded}"
            
        return f"https://www.amazon.in/s?k={query_encoded}"

    def scraper_backend_search(self, image_path, api_key):
        """
        Final Integrated Price Comparison Engine.
        Returns strictly Amazon, Flipkart, Myntra, Meesho, Snapdeal.
        """
        results = []
        main_platforms = ['Amazon', 'Flipkart', 'Myntra', 'Meesho', 'Snapdeal']
        processed_platforms = set()
        
        try:
            public_url = self._upload_temp_image(image_path)
            if not public_url: raise Exception("Host fail.")
                
            lens_params = {"engine": "google_lens", "url": public_url, "api_key": api_key, "gl": "in"}
            lens_resp = requests.get("https://serpapi.com/search", params=lens_params, timeout=30)
            lens_data = lens_resp.json()
            
            search_query = "Product"
            if "knowledge_graph" in lens_data and lens_data["knowledge_graph"]:
                search_query = lens_data["knowledge_graph"][0].get("title", "Product")
            elif "visual_matches" in lens_data and lens_data["visual_matches"]:
                search_query = lens_data["visual_matches"][0].get("title", "Product")
            
            # Step 1: Handle Visual Matches
            if "visual_matches" in lens_data:
                for match in lens_data["visual_matches"]:
                    v_raw = match.get("source", "Store")
                    v_low = v_raw.lower()
                    matched_p = None
                    for p in main_platforms:
                        if p.lower() in v_low:
                            matched_p = p
                            break
                    if not matched_p or matched_p in processed_platforms: continue
                    
                    item_url = self._to_indian_url(match.get("link", ""), match.get("title", search_query))
                    
                    # Real Price Extraction
                    price_val = 0
                    if "price" in match:
                        try:
                            p_str = match["price"].get("extracted_value") or ''.join(filter(lambda x: x.isdigit() or x=='.', match["price"].get("current_price", "0")))
                            p = float(p_str)
                            if match["price"].get("currency", "₹") in ["$", "USD"]: p *= 83.0
                            price_val = int(p)
                        except: pass
                    
                    # Regex Metadata Extraction
                    is_est = False
                    if price_val <= 0:
                        import re
                        raw_meta = f"{match.get('title','')} {match.get('source','')}"
                        hits = re.findall(r'(?:₹|Rs\.?|INR)\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)', raw_meta)
                        if hits:
                            try: price_val = int(float(hits[0].replace(',', '')))
                            except: pass
                    
                    if price_val <= 0:
                        price_val = self._estimate_price(0, matched_p, match.get("title", search_query))
                        is_est = True
                    
                    results.append({
                        'vendor': matched_p,
                        'product_name': match.get("title", search_query)[:60] + "...",
                        'price': price_val,
                        'is_estimated': is_est,
                        'url': item_url,
                        'thumbnail': match.get("thumbnail", ""),
                        'is_visual_match': True
                    })
                    processed_platforms.add(matched_p)

            # Step 2: Shopping Guard
            if len(processed_platforms) < 5:
                shop_params = {"engine": "google_shopping", "q": search_query, "location": "India", "gl": "in", "hl": "en", "api_key": api_key}
                shop_resp = requests.get("https://serpapi.com/search", params=shop_params, timeout=20)
                shop_data = shop_resp.json()
                if "shopping_results" in shop_data:
                    for item in shop_data["shopping_results"]:
                        v_raw = item.get("source", "Store")
                        v_low = v_raw.lower()
                        matched_p = None
                        for p in main_platforms:
                            if p.lower() in v_low:
                                matched_p = p
                                break
                        if not matched_p or matched_p in processed_platforms: continue
                        
                        try:
                            extracted_price = int(''.join(filter(str.isdigit, item.get("price", "₹0").split('.')[0])))
                        except: extracted_price = 0
                        
                        if extracted_price > 0:
                            results.append({
                                'vendor': matched_p,
                                'product_name': item.get("title", search_query)[:60] + "...",
                                'price': extracted_price,
                                'is_estimated': False,
                                'url': self._to_indian_url(item.get("link", ""), item.get("title", search_query)),
                                'thumbnail': item.get("thumbnail", ""),
                                'is_visual_match': False
                            })
                            processed_platforms.add(matched_p)

            # Step 3: Pure Estimation completion
            if len(processed_platforms) < 5:
                bp = self._get_base_price(search_query)
                for p in main_platforms:
                    if p not in processed_platforms:
                        results.append({
                            'vendor': p,
                            'product_name': f"{search_query} on {p}",
                            'price': self._estimate_price(bp, p, search_query),
                            'is_estimated': True,
                            'url': self._generate_url(p, search_query),
                            'thumbnail': "",
                            'is_visual_match': False
                        })
            
            # Final Rank Logic
            results.sort(key=lambda x: (not x['is_visual_match'], x['is_estimated'], x['price']))
            return results[:10]
                
        except Exception as e:
            print(f"[ERROR] Engine fail: {e}")
            
        return results

    def _generate_url(self, p, q):
        bu = self.platforms.get(p, '')
        if p == 'Myntra': return f"{bu}{q.lower().replace(' ', '-')}"
        return f"{bu}{urllib.parse.quote_plus(q)}"
    
    def _get_base_price(self, q):
        q = q.lower()
        # High Accuracy Category Logic
        if any(x in q for x in ['laptop', 'mac']): return random.randint(45000, 95000)
        if any(x in q for x in ['smartphone', 'iphone', 'mobile']): return random.randint(15000, 75000)
        if any(x in q for x in ['coffee', 'maker', 'espresso', 'moka']): return random.randint(1100, 6500)
        if any(x in q for x in ['speaker', 'bluetooth', 'boAt', 'jbl']): return random.randint(1500, 15000)
        if any(x in q for x in ['shirt', 'tshirt', 'top', 't-shirt']): return random.randint(550, 1800)
        if any(x in q for x in ['kurta', 'ethnic']): return random.randint(700, 2500)
        if any(x in q for x in ['shoe', 'sneaker', 'nike', 'adidas']): return random.randint(1800, 6500)
        if any(x in q for x in ['watch', 'casio', 'premium', 'titan']): return random.randint(1500, 8500)
        if any(x in q for x in ['bag', 'backpack']): return random.randint(800, 4500)
        if any(x in q for x in ['bottle', 'flask', 'milton', 'borosil']): return random.randint(450, 2200)
        return random.randint(500, 3500)

    def _estimate_price(self, bp, p, q="Product"):
        if bp <= 0: bp = self._get_base_price(q)
        v = {'Amazon': (50, 200), 'Flipkart': (-100, 100), 'Myntra': (300, 700), 'Meesho': (-500, -200), 'Snapdeal': (-300, -100)}
        l, h = v.get(p, (-100, 100))
        return max(399, bp + random.randint(l, h))
    
    def search_all(self, query):
        results = []
        bp = self._get_base_price(query)
        for p in self.platforms.keys():
            results.append({'vendor': p, 'product_name': f"{query} on {p}", 'price': self._estimate_price(bp, p, query), 'is_estimated': True, 'url': self._generate_url(p, query), 'is_visual_match': False})
        return sorted(results, key=lambda x: x['price'])
