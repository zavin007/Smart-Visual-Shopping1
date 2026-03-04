import streamlit as st
import pandas as pd
from PIL import Image
from src.feature_extractor import FeatureExtractor
from src.recommender import Recommender
from src.scraper import WebScraper
from src.smart_recognizer import SmartProductRecognizer
from src.bg_shader import inject_shader_background
import os

# Page Config
st.set_page_config(page_title="VisionCart AI", page_icon="🛍️", layout="wide")

# --- Sidebar Settings ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    dark_mode = st.toggle("🌙 Dark Mode", value=False)
    learning_mode = st.toggle("🧠 Learning Mode", value=True, help="When ON, uploaded images are added to the database for future searches")
    
    if learning_mode:
        st.success("📚 AI will learn from your uploads!")
        
    # Hardcoded API Key (Hidden from UI for cleaner presentation)
    # Get a free key at serpapi.com and paste it between the quotes below
    serpapi_key = "b812872ae05ca9ba5e74409cc5a8351716e3e3e627ca9a6534e43b7e8b5010a2" 
    
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
    # Modern Dark Theme
    st.markdown("""
    <style>
        
        /* Titles and Text */
        h1, h2, h3, h4, h5, h6, .stMarkdown, p, span, label, div {
            color: #ffffff !important;
            font-family: 'Helvetica Neue', sans-serif;
        }
        
        /* Glassmorphism Containers - Invisible Boundaries */
        [data-testid="stVerticalBlock"] > div:not(:has(style)):not(:has(iframe)) {
            background: rgba(20, 20, 20, 0.2);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            border: none !important;
            padding: 20px;
            box-shadow: none !important;
        }
        
        /* Premium Buttons */
        .stButton>button {
            background: linear-gradient(45deg, #FF512F 0%, #DD2476 100%);
            color: white;
            border: none;
            border-radius: 30px;
            padding: 12px 30px;
            font-size: 16px;
            font-weight: 600;
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
    # Modern Light Theme
    st.markdown("""
    <style>
        /* Force text colors to be dark and readable */
        h1, h2, h3, h4, h5, h6, .stMarkdown, p, span, label, div {
            color: #1a1a1a !important;
        }
        /* Glassmorphism Containers - Invisible Boundaries */
        [data-testid="stVerticalBlock"] > div:not(:has(style)):not(:has(iframe)) {
            background: rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            border: none !important;
            padding: 20px;
            box-shadow: none !important;
        }
        
        /* Premium Buttons */
        .stButton>button {
            background: linear-gradient(45deg, #1fa2ff 0%, #12d8fa 50%, #a6ffcb 100%);
            color: #004d40;
            border: none;
            border-radius: 30px;
            padding: 12px 30px;
            font-size: 16px;
            font-weight: 700;
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
    </style>
    """, unsafe_allow_html=True)


st.title("🛍️ Smart Visual Shopping & Price Discovery")
st.markdown("Upload a product image to find the lowest price across platforms (Amazon, Flipkart, Myntra).")


# Initialize Engine
@st.cache_resource
def load_engine_v2():
    fe = FeatureExtractor()
    recognizer = SmartProductRecognizer()
    try:
        rec = Recommender()
    except Exception as e:
        return fe, None, recognizer
    return fe, rec, recognizer

fe, rec, recognizer = load_engine_v2()

if not rec:
    st.error("⚠️ Data index not found! Please run the data setup script first.")
    st.code("python create_data.py")
    st.stop()

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
                
                # 2. Find closest match in DB (for showing similar product)
                product_id, match_img_path, dist = rec.find_similar(query_feat)
                
                # 3. Use Smart AI to identify the product
                # This uses OCR for brands + BLIP for description + classifier for category
                analysis = recognizer.analyze(image)
                search_query = analysis['search_query']
                product_category = analysis['category'] or search_query
                confidence = analysis['confidence']
                detected_brands = analysis.get('brands', [])
                
                # Show what AI detected
                if detected_brands:
                    st.success(f"🏷️ Brand detected: **{', '.join(detected_brands)}**")
                if analysis['caption']:
                    st.info(f"🤖 AI sees: *{analysis['caption']}*")
                
                st.session_state['match_img'] = match_img_path
                st.session_state['product_name'] = product_category
                st.session_state['confidence'] = confidence
                st.session_state['search_query'] = search_query
                
                # --- ONLINE LEARNING: Save to database if enabled ---
                if learning_mode:
                    success, result = add_to_database(image, search_query)
                    if success:
                        st.toast(f"📚 Learned: {result}", icon="✅")
                    else:
                        st.toast(f"Learning skipped: {result}", icon="⚠️")
            
            # 4. Search using AI-detected product description or Google Lens
            temp_path = "temp_query.jpg"
            image.convert("RGB").save(temp_path, "JPEG")
            
            with st.spinner(f'🌐 Searching for best prices...'):
                try:
                    scraper = WebScraper()
                    if serpapi_key:
                        st.info("🔍 Initializing Deep Web Visual Search...")
                        live_results = scraper.scraper_backend_search(temp_path, serpapi_key)
                    else:
                        live_results = scraper.search_all(search_query)
                    
                    if live_results:
                        results = pd.DataFrame(live_results)
                        best_deal = results.iloc[0]  # Already sorted by price
                        st.session_state['results'] = results
                        st.session_state['best_deal'] = best_deal
                        st.session_state['searched'] = True
                        st.session_state['is_live'] = True
                    else:
                        st.warning("No live results found. Using database fallback.")
                        results = df_local[df_local['product_id'] == product_id].sort_values(by='price')
                        best_deal = results.iloc[0]
                        st.session_state['results'] = results
                        st.session_state['best_deal'] = best_deal
                        st.session_state['searched'] = True
                        st.session_state['is_live'] = False
                except Exception as e:
                    st.error(f"Live search failed: {e}")
                    st.info("Falling back to database...")
                    results = df_local[df_local['product_id'] == product_id].sort_values(by='price')
                    best_deal = results.iloc[0]
                    st.session_state['results'] = results
                    st.session_state['best_deal'] = best_deal
                    st.session_state['searched'] = True
                    st.session_state['is_live'] = False

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
            # Prioritize live thumbnail over low-res local db image
            display_img = item.get('thumbnail') if isinstance(item, dict) and item.get('thumbnail') else st.session_state['match_img']
            st.image(display_img, caption="Visual Match", width=150)
            
        with match_col_b:
            item = st.session_state['best_deal']
            product_display_name = st.session_state.get('product_name', item.get('product_name', 'Unknown'))
            st.markdown(f"**Identified Product:** {product_display_name}")
            st.success(f"🔥 **Best Deal:** ₹{item['price']} on {item['vendor']}")
        
        st.write("---")
        st.subheader("📊 Price Comparison")
        
        # Pretty List with Buy Buttons
        res_df = st.session_state['results'].copy()
        
        st.markdown("### 🏷️ Vendor Options")
        for index, row in res_df.iterrows():
            # Highlight best deal card
            is_best = (row['price'] == res_df.iloc[0]['price'])
            
            with st.container():
                # layout
                c1, c2, c3 = st.columns([2, 1, 1])
                
                with c1:
                    if is_best:
                        st.markdown(f"**{row['vendor']}**  Start ⭐ (Best Price)")
                    else:
                        st.markdown(f"**{row['vendor']}**")
                
                with c2:
                    st.markdown(f"**₹{row['price']}**")
                    
                with c3:
                    st.link_button("Buy Now 🔗", row['url'])
                
                st.divider()
        
        # Mock savings
        savings = res_df.iloc[-1]['price'] - res_df.iloc[0]['price']
        if savings > 0:
            st.info(f"💡 You save **₹{savings}** by buying from {res_df.iloc[0]['vendor']}!")

    else:
        st.info("👈 Upload an image to start searching.")
        
        st.markdown("---")
        st.markdown("### 🛍️ Live Price Discovery Showcase")
        st.markdown("Watch how VisionCart finds the best deals across the internet in real-time.")
        
        # Auto-playing mock carousel
        import time as time_module
        import math
        
        # Define 3 exciting demo products
        demo_products = [
            {
                "name": "Nike Air Max 270",
                "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop",
                "prices": [("Amazon", 12999), ("Flipkart", 11499), ("Myntra", 13200)],
                "desc": "Detecting features: Mesh upper, Air unit..."
            },
            {
                "name": "Sony WH-1000XM5",
                "image": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?q=80&w=600&auto=format&fit=crop",
                "prices": [("Amazon", 29990), ("Croma", 32000), ("Reliance", 28500)],
                "desc": "Analyzing shape: Over-ear, matte finish..."
            },
            {
                "name": "Apple Watch Series 9",
                "image": "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?q=80&w=600&auto=format&fit=crop",
                "prices": [("Amazon", 41900), ("Flipkart", 40500), ("Apple", 41900)],
                "desc": "Identifying brand: Apple, aluminum case..."
            }
        ]
        
        # Cycle through them based on current time
        cycle_time = 4.0 # seconds per slide
        current_idx = int(math.floor(time_module.time() / cycle_time)) % len(demo_products)
        product = demo_products[current_idx]
        
        # Render the showcase card
        with st.container():
            st.markdown(f"#### 🔍 Live Scan: **{product['name']}**")
            
            c1, c2 = st.columns([1, 1.5])
            with c1:
                st.image(product['image'], use_container_width=True, caption=product['desc'])
            
            with c2:
                # Find the lowest price
                best_price = min([p[1] for p in product['prices']])
                
                for vendor, price in product['prices']:
                    if price == best_price:
                        st.success(f"🔥 **{vendor}**: ₹{price:,} (Best Deal!)")
                    else:
                        st.info(f"🏬 **{vendor}**: ₹{price:,}")
                        
        # Auto-rerun trick to make the carousel animate
        time_module.sleep(1)
        st.rerun()
