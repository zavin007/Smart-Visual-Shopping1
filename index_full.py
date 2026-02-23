"""
Full Dataset Indexer
Copies ALL 33,000 Kaggle images to the store and indexes them.
This will take 45-60 minutes. Let it run in the background.
"""
import os
import shutil
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from tqdm import tqdm
from src.feature_extractor import FeatureExtractor

# Paths
BASE_DIR = Path.cwd()
SOURCE_DIR = BASE_DIR / "data" / "fashion-dataset" / "organized"
DEST_DIR = BASE_DIR / "data" / "images"
DATA_DIR = BASE_DIR / "data"

def get_product_id(filename):
    """Consistent ID generation"""
    stem = os.path.splitext(filename)[0]
    try:
        pid = int(stem.split('_')[0])
    except:
        pid = abs(hash(stem)) % 100000
    return pid

def main():
    print("=" * 60)
    print("   FULL DATASET INDEXER - 33,000 Products")
    print("=" * 60)
    
    # 1. Clean destination
    print("\n[Step 1/4] Cleaning store...")
    if DEST_DIR.exists():
        for f in DEST_DIR.glob("*"):
            try:
                os.remove(f)
            except:
                pass
    else:
        DEST_DIR.mkdir(parents=True)
    
    # 2. Copy ALL images
    print("\n[Step 2/4] Copying all products to store...")
    all_images = list(SOURCE_DIR.rglob("*.jpg"))
    print(f"   Found {len(all_images)} images in source.")
    
    copied = 0
    for src in tqdm(all_images, desc="Copying"):
        try:
            dst = DEST_DIR / src.name
            shutil.copy2(src, dst)
            copied += 1
        except Exception as e:
            pass
    
    print(f"   Copied {copied} images to store.")
    
    # 3. Generate Price Database
    print("\n[Step 3/4] Generating price database...")
    image_files = [f for f in os.listdir(DEST_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    price_data = []
    vendors = ["Amazon", "Flipkart", "Myntra"]
    
    for img_file in tqdm(image_files, desc="Prices"):
        pid = get_product_id(img_file)
        p_name = f"Fashion Item {pid}"
        base_price = np.random.randint(500, 5000)
        
        for v in vendors:
            price = base_price + np.random.randint(-200, 200)
            price = max(199, price)
            price_data.append({
                "product_id": pid,
                "product_name": p_name,
                "vendor": v,
                "price": price,
                "url": f"https://www.{v.lower()}.com/p/{pid}",
                "filename": img_file
            })
    
    df = pd.DataFrame(price_data)
    df.to_csv(DATA_DIR / "product_prices.csv", index=False)
    print(f"   Created price database with {len(df)} entries.")
    
    # 4. Extract Features (This is the slow part)
    print("\n[Step 4/4] Extracting visual features (this takes ~45 min)...")
    fe = FeatureExtractor()
    features = []
    img_paths = []
    ids = []
    
    image_files = [f for f in os.listdir(DEST_DIR) if f.endswith('.jpg')]
    
    for img_file in tqdm(image_files, desc="Features"):
        img_path = os.path.join(DEST_DIR, img_file)
        
        try:
            feat = fe.extract(img_path)
            features.append(feat)
            img_paths.append(img_path)
            ids.append(get_product_id(img_file))
        except Exception as e:
            continue
    
    # Save
    features = np.array(features)
    pickle.dump(features, open(DATA_DIR / "features.pkl", "wb"))
    pickle.dump(ids, open(DATA_DIR / "ids.pkl", "wb"))
    pickle.dump(img_paths, open(DATA_DIR / "img_paths.pkl", "wb"))
    
    print("\n" + "=" * 60)
    print(f"   DONE! Indexed {len(features)} products.")
    print("   Restart your app: streamlit run app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
