"""
Enhanced Product Recognition Module
Uses multiple strategies to get the best search query:
1. Hugging Face BLIP model for image captioning (FREE, no API key)
2. Local classifier for product category
3. OCR for brand/text detection
4. Smart keyword extraction
"""
import os
import json
import re
import numpy as np
from PIL import Image

# Try to import easyocr for text detection
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[INFO] EasyOCR not installed. Brand text detection disabled.")
    print("       To enable: pip install easyocr")

# Try to import transformers for BLIP model
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    BLIP_AVAILABLE = True
except ImportError:
    BLIP_AVAILABLE = False
    print("[INFO] Transformers not installed. Using basic classification only.")
    print("       To enable smart descriptions: pip install transformers torch")

# Try to import local classifier
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

# Known brands for matching
KNOWN_BRANDS = [
    'nike', 'adidas', 'puma', 'reebok', 'new balance', 'converse', 'vans', 'fila',
    'samsung', 'apple', 'sony', 'lg', 'oneplus', 'xiaomi', 'realme', 'oppo', 'vivo',
    'casio', 'titan', 'fastrack', 'fossil', 'timex', 'rolex', 'omega',
    'ray-ban', 'oakley', 'gucci', 'prada', 'versace', 'armani',
    'bata', 'woodland', 'red tape', 'liberty', 'paragon',
    'levis', 'lee', 'wrangler', 'pepe jeans', 'flying machine',
    'peter england', 'van heusen', 'allen solly', 'louis philippe',
    'hp', 'dell', 'lenovo', 'asus', 'acer', 'msi',
    'boat', 'jbl', 'bose', 'sennheiser', 'sony',
    'parker', 'mont blanc', 'cross', 'waterman', 'sheaffer'
]


class SmartProductRecognizer:
    """
    Combines multiple AI methods for accurate product identification.
    """
    
    def __init__(self):
        self.blip_processor = None
        self.blip_model = None
        self.local_classifier = None
        self.ocr_reader = None
        self.class_names = {}
        
        self._load_ocr()
        self._load_blip()
        self._load_local_classifier()
    
    def _load_ocr(self):
        """Load EasyOCR for text/brand detection"""
        if not OCR_AVAILABLE:
            return
            
        try:
            print("[INFO] Loading OCR for brand detection...")
            use_gpu = torch.cuda.is_available() if BLIP_AVAILABLE else False
            self.ocr_reader = easyocr.Reader(['en'], gpu=use_gpu, verbose=False)
            print(f"[OK] OCR loaded successfully! (GPU: {use_gpu})")
        except Exception as e:
            print(f"[WARN] Could not load OCR: {e}")
    
    def detect_text_brands(self, image):
        """
        Use OCR to detect brand names in the image.
        Returns: list of detected brand names
        """
        if not self.ocr_reader:
            return []
            
        try:
            if isinstance(image, str):
                image = Image.open(image)
            
            # Convert to numpy array for OCR
            img_array = np.array(image.convert('RGB'))
            
            # Run OCR
            results = self.ocr_reader.readtext(img_array)
            
            detected_brands = []
            all_text = []
            
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Only high confidence text
                    all_text.append(text.lower())
            
            # Check for known brands
            combined_text = " ".join(all_text)
            for brand in KNOWN_BRANDS:
                if brand in combined_text:
                    detected_brands.append(brand.title())
                    print(f"[OCR] Detected brand: {brand.title()}")
            
            # Also return raw text for potential model/product names
            return detected_brands, all_text
        except Exception as e:
            print(f"[WARN] OCR error: {e}")
            return [], []
    
    def _load_blip(self):
        """Load BLIP image captioning model"""
        if not BLIP_AVAILABLE:
            return
            
        try:
            print("[INFO] Loading BLIP image captioning model...")
            # Use smaller BLIP model for faster inference and float16 for massive speedup on GPU
            model_name = "Salesforce/blip-image-captioning-base"
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if self.device == "cuda" else torch.float32
            
            self.blip_processor = BlipProcessor.from_pretrained(model_name)
            self.blip_model = BlipForConditionalGeneration.from_pretrained(
                model_name, torch_dtype=dtype
            ).to(self.device)
            print(f"[OK] BLIP model loaded successfully on {self.device.upper()} (dtype: {dtype})!")
        except Exception as e:
            print(f"[WARN] Could not load BLIP model: {e}")
    
    def _load_local_classifier(self):
        """Load local fashion classifier as fallback"""
        if not TF_AVAILABLE:
            return
            
        model_path = "trained_model.keras"
        class_path = "class_indices.json"
        
        if os.path.exists(model_path) and os.path.exists(class_path):
            try:
                self.local_classifier = tf.keras.models.load_model(model_path)
                with open(class_path, 'r') as f:
                    indices = json.load(f)
                self.class_names = {v: k.replace('_', ' ') for k, v in indices.items()}
                print(f"[OK] Local classifier loaded with {len(self.class_names)} categories")
            except Exception as e:
                print(f"[WARN] Could not load local classifier: {e}")
    
    def get_blip_caption(self, image):
        """
        Use BLIP to generate a natural description of the product.
        Returns: "a pair of nike running shoes", "a silver wristwatch", etc.
        """
        if not self.blip_model or not self.blip_processor:
            return None
            
        try:
            # Prepare image
            if isinstance(image, str):
                image = Image.open(image)
            image = image.convert('RGB')
            
            # Generate caption with product-focused prompt
            if hasattr(self, 'device'):
                inputs = self.blip_processor(image, "a photo of", return_tensors="pt").to(self.device)
            else:
                inputs = self.blip_processor(image, "a photo of", return_tensors="pt")
            
            with torch.no_grad():
                output = self.blip_model.generate(**inputs, max_length=30)
            
            caption = self.blip_processor.decode(output[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            print(f"[WARN] BLIP caption error: {e}")
            return None
    
    def get_local_classification(self, image):
        """
        Use local trained model to classify product category.
        Returns: ("Casual Shoes", 0.85)
        """
        if not self.local_classifier:
            return None, 0.0
            
        try:
            if isinstance(image, str):
                image = Image.open(image)
            
            img = image.convert('RGB').resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            predictions = self.local_classifier.predict(img_array, verbose=0)
            class_idx = np.argmax(predictions[0])
            confidence = predictions[0][class_idx]
            
            category = self.class_names.get(class_idx, "Product")
            return category, float(confidence)
        except Exception as e:
            print(f"[WARN] Local classification error: {e}")
            return None, 0.0
    
    def extract_keywords(self, text):
        """
        Extract product-relevant keywords from text.
        """
        if not text:
            return []
        
        # Common brands to look for
        brands = ['nike', 'adidas', 'puma', 'reebok', 'samsung', 'apple', 'sony', 
                  'casio', 'titan', 'fastrack', 'ray-ban', 'fossil', 'boat', 'jbl',
                  'bata', 'woodland', 'levi', 'peter england', 'van heusen', 'allen solly']
        
        # Product types
        product_types = ['shoes', 'watch', 'bag', 'wallet', 'sunglasses', 'shirt', 
                        'jeans', 'tshirt', 'sneakers', 'sandals', 'heels', 'kurta',
                        'backpack', 'handbag', 'belt', 'pen', 'bottle', 'phone']
        
        text_lower = text.lower()
        found = []
        
        # Find brands
        for brand in brands:
            if brand in text_lower:
                found.append(brand.title())
                break
        
        # Find product types
        for ptype in product_types:
            if ptype in text_lower:
                found.append(ptype.title())
                break
        
        return found
    
    def get_search_query(self, image):
        """
        Main method: Get the best possible search query for the product.
        
        Strategy:
        1. Try OCR first to detect brand names (most accurate for branded products)
        2. Try BLIP caption for product description
        3. Fall back to local classifier for category
        4. Combine: Brand + Category for optimal query
        """
        brands_found = []
        category_found = None
        
        # 1. Try OCR to detect brand text
        ocr_brands, raw_text = self.detect_text_brands(image)
        if ocr_brands:
            brands_found.extend(ocr_brands)
        
        # 2. Try BLIP caption for product type understanding
        caption = self.get_blip_caption(image)
        if caption:
            print(f"[BLIP] Caption: {caption}")
            keywords = self.extract_keywords(caption)
            for kw in keywords:
                if kw not in brands_found:
                    if not category_found:
                        category_found = kw
        
        # 3. Try local classifier for product category
        category, confidence = self.get_local_classification(image)
        if category and confidence > 0.3:
            print(f"[LOCAL] Category: {category} ({confidence:.0%})")
            if not category_found:
                category_found = category
        
        # 4. Build optimal search query
        # Priority: Brand + Category (e.g., "Nike Casual Shoes")
        query_parts = []
        
        if brands_found:
            query_parts.append(brands_found[0])  # Use first detected brand
        
        if category_found:
            query_parts.append(category_found)
        elif caption:
            # Use cleaned caption if no category
            clean = caption.replace("a photo of", "").strip()
            if len(clean) > 3 and clean not in query_parts:
                query_parts.append(clean)
        
        if query_parts:
            return " ".join(query_parts)
        else:
            return "Fashion Product"
    
    def analyze(self, image):
        """
        Full analysis of an image.
        Returns dict with all detected information.
        """
        result = {
            'caption': None,
            'category': None,
            'brands': [],
            'confidence': 0.0,
            'search_query': 'Product'
        }
        
        # Get OCR brands first
        brands, raw_text = self.detect_text_brands(image)
        result['brands'] = brands
        
        # Get BLIP caption
        caption = self.get_blip_caption(image)
        if caption:
            result['caption'] = caption
        
        # Get local classification
        category, confidence = self.get_local_classification(image)
        result['category'] = category
        result['confidence'] = confidence
        
        # Get search query (uses all methods internally)
        result['search_query'] = self.get_search_query(image)
        
        return result


# Singleton for app use
_recognizer = None

def get_recognizer():
    global _recognizer
    if _recognizer is None:
        _recognizer = SmartProductRecognizer()
    return _recognizer


# Test
if __name__ == "__main__":
    recognizer = SmartProductRecognizer()
    
    # Test with a sample image
    test_dir = "data/images"
    if os.path.exists(test_dir):
        samples = os.listdir(test_dir)[:3]
        for img_name in samples:
            img_path = os.path.join(test_dir, img_name)
            print(f"\n--- Testing: {img_name} ---")
            result = recognizer.analyze(img_path)
            print(f"Caption: {result['caption']}")
            print(f"Category: {result['category']} ({result['confidence']:.0%})")
            print(f"Search Query: {result['search_query']}")
