import streamlit as st
import pandas as pd
from PIL import Image
from src.bg_shader import inject_shader_background
import os

# Page Config
st.set_page_config(page_title="VisionCart AI", page_icon="🛍️", layout="wide")

# --- PWA Manifest & Service Worker ---
st.markdown("""
<link rel="manifest" href="./static/manifest.json">
<meta name="theme-color" content="#7c3aed">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="VisionCart AI">
<link rel="apple-touch-icon" href="./static/icon-192.png">
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./static/sw.js')
    .then(reg => console.log('VisionCart SW registered:', reg.scope))
    .catch(err => console.log('SW registration failed:', err));
}
</script>
""", unsafe_allow_html=True)

# --- Sidebar Settings ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    dark_mode = st.toggle("🌙 Dark Mode", value=False)
        
    # Secure API Key Management
    serpapi_key = st.secrets.get("SERPAPI_KEY", os.getenv("SERPAPI_KEY", ""))
    
# Always apply WebGL Background
inject_shader_background()
st.markdown("""
<style>
    .stApp {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


# Apply Dark Mode CSS
# Apply Premium Styling
if dark_mode:
    # Modern Dark Theme + Custom Fonts
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;700;800&display=swap');
        
        /* Apply Base Font */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* stylize headers with maximum contrast */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            color: #ffffff !important;
            font-weight: 800 !important;
        }
        
        /* Make body text extremely readable */
        p, .stMarkdown p, span, label {
            color: #ffffff !important;
            font-size: 1.15rem !important;
            font-weight: 600 !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        }
        
        /* Premium Buttons - Bold text */
        .stButton>button {
            background: linear-gradient(45deg, #FF512F 0%, #DD2476 100%);
            color: white !important;
            border: none;
            border-radius: 30px;
            padding: 12px 30px;
            font-size: 18px;
            font-weight: 800;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(221, 36, 118, 0.4);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(221, 36, 118, 0.6);
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(10, 10, 10, 0.9);
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Sidebar Toggle Button Fix */
        button[kind="header"] {
            background-color: rgba(20, 20, 20, 0.5) !important;
            border-radius: 50% !important;
            box-shadow: 0 0 10px rgba(255,255,255,0.2) !important;
            backdrop-filter: blur(5px);
        }
        button[kind="header"] svg, 
        [data-testid="collapsedControl"] svg,
        .st-emotion-cache-1vt4ygl svg {
            fill: #ffffff !important;
            color: #ffffff !important;
            stroke: #ffffff !important;
        }
        
        /* Input Fields */
        .stTextInput>div>div>input {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* Success/Info Messages */
        .stSuccess, .stInfo, .stWarning {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* File Uploader - Dark Mode Fix */
        [data-testid="stFileUploader"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 20px;
            border: 2px dashed rgba(255,255,255,0.3);
        }
        [data-testid="stFileUploader"] label,
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] p,
        [data-testid="stFileUploader"] small {
            color: #ffffff !important;
            font-weight: 500;
        }
        [data-testid="stFileUploader"] button {
            background: #ffffff !important;
            color: #764ba2 !important;
            border-radius: 20px;
            font-weight: bold;
            border: none;
        }
        [data-testid="stFileUploader"] section {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # Modern Light Theme + Custom Fonts
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;700;800&display=swap');
        
        /* Apply Base Font */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Stylize Headers for Light Mode - Extreme Dark */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            color: #000000 !important;
            font-weight: 800 !important;
        }
        
        /* Black, heavy text for light mode */
        p, .stMarkdown p, span, label {
            color: #000000 !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
        }
        
        /* Glassmorphism Containers */
        [data-testid="stVerticalBlock"] > div:not(:has(style)):not(:has(iframe)) {
            background: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1px solid rgba(0,0,0,0.1);
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1) !important;
        }
        
        /* Premium Buttons */
        .stButton>button {
            background: linear-gradient(45deg, #1fa2ff 0%, #12d8fa 50%, #a6ffcb 100%);
            color: #000000 !important;
            border: none;
            border-radius: 30px;
            padding: 12px 30px;
            font-size: 18px;
            font-weight: 800;
            box-shadow: 0 4px 15px rgba(18, 216, 250, 0.3);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(18, 216, 250, 0.5);
        }
        
        .stSuccess {
            background: #d4edda !important;
            color: #155724 !important;
            border-radius: 12px;
        }
        
        /* === MOBILE RESPONSIVE FIXES === */
        @media (max-width: 768px) {
            /* Remove heavy glass cards on mobile */
            [data-testid="stVerticalBlock"] > div:not(:has(style)):not(:has(iframe)) {
                background: rgba(255, 255, 255, 0.15) !important;
                backdrop-filter: blur(8px) !important;
                -webkit-backdrop-filter: blur(8px) !important;
                padding: 10px !important;
                border: 1px solid rgba(255,255,255,0.15) !important;
                box-shadow: none !important;
            }
            
            /* Fix file uploader dark shadow on mobile */
            [data-testid="stFileUploader"] {
                background: rgba(255, 255, 255, 0.2) !important;
                border: 2px dashed rgba(255,255,255,0.4) !important;
                border-radius: 12px !important;
                padding: 12px !important;
            }
            [data-testid="stFileUploader"] section {
                background: rgba(255,255,255,0.15) !important;
            }
            [data-testid="stFileUploader"] label,
            [data-testid="stFileUploader"] span,
            [data-testid="stFileUploader"] p,
            [data-testid="stFileUploader"] small {
                color: #ffffff !important;
            }
            
            /* Expand camera viewport on mobile */
            [data-testid="stCameraInput"] video,
            [data-testid="stCameraInput"] img,
            [data-testid="stCameraInput"] canvas {
                width: 100% !important;
                max-width: 100% !important;
                height: auto !important;
                min-height: 300px !important;
                object-fit: cover !important;
                border-radius: 12px !important;
            }
            [data-testid="stCameraInput"] {
                width: 100% !important;
            }
            [data-testid="stCameraInput"] > div {
                width: 100% !important;
            }
            
            /* Shrink title for mobile */
            .main-title {
                font-size: 2rem !important;
                letter-spacing: -1px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)


st.markdown("""
<style>
    .main-title {
        color: #FFFFFF !important;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        letter-spacing: -2px !important;
        line-height: 1.1 !important;
        margin-bottom: 10px !important;
        font-family: 'Outfit', sans-serif !important;
    }
</style>
<div class="main-title">🛍️ Smart Visual Shopping & Price Discovery</div>
""", unsafe_allow_html=True)
st.markdown("""
<style>
    .white-text p {
        color: #ffffff !important;
    }
</style>
<div class="white-text">
    <p style="font-size: 1.1rem; font-weight: 500;">Upload a product image to find the lowest price across platforms (Amazon, Flipkart, Myntra).</p>
</div>
""", unsafe_allow_html=True)


# Initialize Engine — Load each model separately to prevent memory spikes
@st.cache_resource
def load_feature_extractor():
    from src.feature_extractor import FeatureExtractor
    return FeatureExtractor()

@st.cache_resource
def load_recommender():
    from src.recommender import Recommender
    return Recommender()

@st.cache_resource
def load_recognizer():
    from src.smart_recognizer import SmartProductRecognizer
    return SmartProductRecognizer()

# Load models in stages with progress feedback
engine_placeholder = st.empty()
with engine_placeholder.status("🧠 Loading AI Engine...", expanded=True) as status:
    status.update(label="📦 Loading Feature Extractor (MobileNetV4)...")
    fe = load_feature_extractor()
    
    status.update(label="📦 Loading Recommender Engine...")
    try:
        rec = load_recommender()
    except Exception:
        rec = None
    
    status.update(label="📦 Loading Smart Recognizer (BLIP + EasyOCR)...")
    recognizer = load_recognizer()

engine_placeholder.empty()

# Load local offline data
@st.cache_data
def load_local_prices():
    try:
        return pd.read_csv("data/product_prices.csv")
    except:
        return None

df_local = load_local_prices()

# --- Cloud Deployment Check ---
# On Hugging Face (Cloud), we don't have the 40k image dataset.
# We will run in 'Online-Only' mode if the index is missing.
cloud_mode = False
if not rec or df_local is None:
    cloud_mode = True

# --- Online Learning: Add image to database ---
import numpy as np
import time as time_module

def add_to_database(image, search_query):
    """
    Save uploaded image to database and update feature index.
    This allows the system to 'learn' from new uploads.
    """
    try:
        # Generate unique filename
        timestamp = int(time_module.time() * 1000)
        clean_name = search_query.replace(' ', '_').replace('/', '_')[:30]
        filename = f"{clean_name}_{timestamp}.jpg"
        save_path = os.path.join("data", "images", filename)
        
        # Ensure directory exists
        os.makedirs(os.path.join("data", "images"), exist_ok=True)
        
        # Save image
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(save_path, 'JPEG', quality=90)
        
        # Extract features
        features = fe.extract(image)
        
        # Update the database (append to DataFrame)
        features_path = os.path.join("data", "features.pkl")
        if os.path.exists(features_path):
            import pandas as pd
            df = pd.read_pickle(features_path)
            
            # Generate new product ID
            new_id = int(timestamp % 100000)
            
            # Append new entry
            new_row = pd.DataFrame([{
                'product_id': new_id,
                'image_path': save_path,
                'features': features
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save updated database
            df.to_pickle(features_path)
            
            # Reload recommender in next run (clear cache)
            st.cache_resource.clear()
            
            return True, filename
    except Exception as e:
        print(f"[ERROR] Failed to add to database: {e}")
        return False, str(e)
    
    return False, "Unknown error"

# Main Layout
col1, col2 = st.columns([1, 2])

# Main Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📸 Capture or Upload")
    
    # Input Method Selection
    input_method = st.radio("Choose Input:", ["Upload Image", "Use Camera"], horizontal=True)
    
    image_source = None
    
    if input_method == "Upload Image":
        uploaded_file = st.file_uploader("Choose a file...", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            image_source = uploaded_file
    else:
        camera_file = st.camera_input("Take a picture")
        if camera_file:
            image_source = camera_file

    if image_source is not None:
        image = Image.open(image_source)
        st.image(image, caption='Query Image', use_container_width=True)
        
        if st.button('🔍 Find Best Price', type="primary"):
            with st.spinner('🧠 AI is analyzing your product...'):
                # 1. Extract feature for visual matching
                query_feat = fe.extract(image)
                
                # --- IMAGE QUALITY VALIDATION ---
                import numpy as np
                gray = np.array(image.convert("L"), dtype=float)
                # Laplacian variance = measure of sharpness. Low value = blurry.
                laplacian_score = np.var(np.gradient(np.gradient(gray)))
                if laplacian_score < 80:
                    st.error("📷 Your image looks **blurry or unclear**. Please upload a sharper, well-lit photo of the product for best results.")
                    st.stop()
                
                # 2. Find closest match in DB (for showing similar product)
                if not cloud_mode:
                    product_id, match_img_path, dist = rec.find_similar(query_feat)
                else:
                    product_id, match_img_path, dist = None, None, None
                
                # 3. Use Smart AI to identify the product
                # This uses OCR for brands + BLIP for description + classifier for category
                analysis = recognizer.analyze(image)
                search_query = analysis['search_query']
                product_category = analysis['category'] or search_query
                confidence = analysis['confidence']
                detected_brands = analysis.get('brands', [])
                caption = analysis.get('caption', '') or ''
                
                # --- NON-PRODUCT VALIDATION ---
                # If BLIP identifies something that is clearly NOT a product, warn the user.
                non_product_keywords = [
                    'a group of people', 'a man', 'a woman', 'a person', 'a crowd',
                    'a room', 'a building', 'a house', 'a street', 'a road', 'a city',
                    'a field', 'a tree', 'a mountain', 'a sky', 'a dog', 'a cat',
                    'a bird', 'a car', 'a vehicle', 'a landscape', 'nature'
                ]
                caption_lower = caption.lower()
                is_non_product = any(kw in caption_lower for kw in non_product_keywords)
                if is_non_product and not detected_brands:
                    st.warning(f"🖼️ This doesn't look like a product image (AI sees: *\"{caption}\"*). Please upload a **clear photo of a product** like clothing, shoes, accessories, or electronics.")
                    st.stop()

                
                # Show what AI detected
                if detected_brands:
                    st.success(f"🏷️ Brand detected: **{', '.join(detected_brands)}**")
                if analysis['caption']:
                    st.info(f"🤖 AI sees: *{analysis['caption']}*")
                
                st.session_state['match_img'] = match_img_path
                st.session_state['product_name'] = product_category
                st.session_state['confidence'] = confidence
                st.session_state['search_query'] = search_query
                
            
            # 4. Search using AI-detected product description or Google Lens
            temp_path = "temp_query.jpg"
            image.convert("RGB").save(temp_path, "JPEG")
            
            with st.spinner(f'🌐 Searching for best prices...'):
                from src.scraper import WebScraper
                scraper = WebScraper()
                live_results = None
                
                # Strategy 1: Visual-First Search (via Scraper Engine)
                if serpapi_key:
                    try:
                        st.toast("🔍 Running Visual Search...")
                        live_results = scraper.scraper_backend_search(temp_path, serpapi_key)
                    except Exception as e:
                        print(f"Scraper error: {e}")
                        live_results = None
                
                # Strategy 2: Absolute Fallback (Title-based simulated)
                if not live_results:
                    live_results = scraper.search_all(search_query)
                
                # At this point we ALWAYS have results
                results = pd.DataFrame(live_results)
                best_deal = results.iloc[0]
                st.session_state['results'] = results
                st.session_state['best_deal'] = best_deal
                st.session_state['product_name'] = search_query
                st.session_state['searched'] = True
                st.session_state['is_live'] = True

with col2:
    if st.session_state.get('searched'):
        # Show live/database badge
        if st.session_state.get('is_live'):
            st.success("🔴 LIVE RESULTS from Web")
        else:
            st.info("📦 Results from Local Database")
        
        st.subheader("✅ Match Found!")
        
        # Display the matched product info
        match_col_a, match_col_b = st.columns([1, 3])
        with match_col_a:
            item = st.session_state['best_deal']
            # Always show the thumbnail from the best-priced online result
            display_img = item.get('thumbnail') if isinstance(item, dict) else item.get('thumbnail', '')
            if display_img:
                st.image(display_img, caption="Visual Match", width=150)
            else:
                st.markdown("🛍️")
            
        with match_col_b:
            item = st.session_state['best_deal']
            product_display_name = st.session_state.get('product_name', item.get('product_name', 'Unknown'))
            st.markdown(f"**Identified Product:** {product_display_name}")
            st.success(f"🔥 **Best Deal:** ₹{item['price']} on {item['vendor']}")
        
        st.subheader("📊 Price Comparison")
        
        # Pretty List with Buy Buttons
        res_df = st.session_state['results'].copy()
        
        st.markdown("### 🏷️ Vendor Options")
        for index, row in res_df.iterrows():
            # Highlight best deal card
            is_best = (row['price'] == res_df.iloc[0]['price'])
            
            with st.container():
                # layout
                c_img, c1, c2, c3 = st.columns([1, 2, 1, 1])
                
                with c_img:
                    # Try to get live thumbnail or fallback to local image
                    thumb_url = row.get('thumbnail', '')
                    if pd.isna(thumb_url) or not thumb_url:
                        if 'filename' in row and not pd.isna(row['filename']):
                            thumb_url = os.path.join("data", "images", str(row['filename']))
                    
                    if thumb_url:
                        try:
                            st.image(thumb_url, width=50)
                        except:
                            st.markdown("🛍️")
                    else:
                        st.markdown("🛍️")
                
                with c1:
                    if is_best:
                        st.markdown(f"**{row['vendor']}** ⭐ (Best Price)")
                    else:
                        st.markdown(f"**{row['vendor']}**")
                
                with c2:
                    st.markdown(f"**₹{row['price']}**")
                    
                with c3:
                    url = row.get('url', '#')
                    if pd.isna(url): url = '#'
                    st.link_button("Buy Now 🔗", url)
                
                st.divider()
        
        # Mock savings
        savings = res_df.iloc[-1]['price'] - res_df.iloc[0]['price']
        if savings > 0:
            st.info(f"💡 You save **₹{savings}** by buying from {res_df.iloc[0]['vendor']}!")

    else:
        st.info("👈 Upload an image to start searching.")
        
        st.markdown("### 🏷️ Featured Fashion & Live Deals")
        st.markdown("VisionCart finds the best prices across the web in real-time.")

        # Smooth Non-Blinking Carousel using HTML/CSS
        carousel_html = """
        <style>
            .carousel-container {
                width: 100%;
                height: 380px;
                position: relative;
                overflow: hidden;
                border-radius: 20px;
                background: rgba(255,255,255,0.05);
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Inter', sans-serif;
            }
            .slide {
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                opacity: 0;
                transition: opacity 1s ease-in-out;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
                box-sizing: border-box;
                text-align: center;
            }
            .slide.active { opacity: 1; }
            .slide img {
                width: 200px;
                height: 200px;
                object-fit: cover;
                border-radius: 15px;
                box-shadow: 0 10px 20px rgba(0,0,0,0.3);
                margin-bottom: 15px;
            }
            .product-name { color: #fff; font-size: 1.2rem; font-weight: 700; margin: 5px 0; }
            .product-price { color: #00ff88; font-size: 1.1rem; font-weight: 600; }
            .vendor-tag { background: rgba(255,255,255,0.1); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; color: #ddd; margin-top: 10px; }
            .scan-line {
                position: absolute;
                top: 0; left: 0; width: 100%; height: 2px;
                background: rgba(0, 255, 136, 0.5);
                box-shadow: 0 0 15px #00ff88;
                animation: scan 3s linear infinite;
            }
            @keyframes scan {
                0% { top: 10%; }
                50% { top: 70%; }
                100% { top: 10%; }
            }
        </style>
        <div class="carousel-container">
            <div class="scan-line"></div>
            <div class="slide active">
                <img src="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?q=80&w=400&auto=format&fit=crop">
                <div class="product-name">Zara Men's Slim Fit Shirt</div>
                <div class="product-price">₹2,990 <span style="font-size:0.8rem; color:#888;">Live Price Check</span></div>
                <div class="vendor-tag">Found on: Myntra ⭐</div>
            </div>
            <div class="slide">
                <img src="https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=400&auto=format&fit=crop">
                <div class="product-name">Nike Air Max 270</div>
                <div class="product-price">₹10,490 <span style="font-size:0.8rem; color:#888;">15% Discount Appled</span></div>
                <div class="vendor-tag">Found on: Amazon India 🚚</div>
            </div>
            <div class="slide">
                <img src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=400&auto=format&fit=crop">
                <div class="product-name">H&M Summer Floral Dress</div>
                <div class="product-price">₹1,499</div>
                <div class="vendor-tag">Found on: Ajio 🏷️</div>
            </div>
            <div class="slide">
                <img src="https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?q=80&w=400&auto=format&fit=crop">
                <div class="product-name">Adidas Stan Smith sneakers</div>
                <div class="product-price">₹7,999</div>
                <div class="vendor-tag">Found on: Flipkart 📦</div>
            </div>
        </div>
        <script>
            let slides = document.querySelectorAll('.slide');
            let currentSlide = 0;
            function nextSlide() {
                slides[currentSlide].classList.remove('active');
                currentSlide = (currentSlide + 1) % slides.length;
                slides[currentSlide].classList.add('active');
            }
            setInterval(nextSlide, 3500); // Change every 3.5 seconds
        </script>
        """
        import streamlit.components.v1 as components
        components.html(carousel_html, height=390)
