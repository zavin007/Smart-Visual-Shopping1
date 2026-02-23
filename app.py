import streamlit as st
import pandas as pd
from PIL import Image
from src.feature_extractor import FeatureExtractor
from src.recommender import Recommender
from src.scraper import WebScraper
from src.smart_recognizer import SmartProductRecognizer
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
    


# Apply Dark Mode CSS
# Apply Premium Styling
if dark_mode:
    # Modern Dark Theme
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1604014237800-1c9102c219da?q=80&w=1920&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* Titles and Text */
        h1, h2, h3, h4, h5, h6, .stMarkdown, p, span, label {
            color: #ffffff !important;
            font-family: 'Helvetica Neue', sans-serif;
        }
        
        /* Glassmorphism Containers */
        [data-testid="stVerticalBlock"] > div {
            background: rgba(20, 20, 20, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
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
        .stApp {
            background: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), url("https://images.unsplash.com/photo-1557821552-17105176677c?q=80&w=1920&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* Glassmorphism Containers */
        [data-testid="stVerticalBlock"] > div {
            background: rgba(255, 255, 255, 0.65);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.4);
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
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
            
            # 4. Search using AI-detected product description
            with st.spinner(f'🌐 Searching "{search_query}" across 5 platforms...'):
                try:
                    scraper = WebScraper()
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
            st.image(st.session_state['match_img'], caption="Visual Match", width=150)
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
        st.markdown("""
        ### How it works:
        1. **Deep Learning (CNN)** extracts features from your image.
        2. **Nearest Neighbors** finds the exact product in our database.
        3. **Price Aggregator** fetches real-time (simulated) prices from vendors.
        """)
