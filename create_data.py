import os
import numpy as np
import pandas as pd
import pickle
from tqdm import tqdm
from src.feature_extractor import FeatureExtractor

# Config
DATA_DIR = "data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

def get_product_id(filename):
    """Consistent ID generation from filename"""
    stem = os.path.splitext(filename)[0]
    try:
        # Try finding the first numeric part
        pid = int(stem.split('_')[0])
    except:
        # Robust fallback
        pid = abs(hash(stem)) % 100000
    return pid

def create_price_database(image_files):
    """
    Generates product_prices.csv based on available images.
    This is required for the frontend app to display price info.
    """
    print("Generating price data for inventory...")
    price_data = []
    vendors = ["Amazon", "Flipkart", "Myntra"]
    
    for img_file in image_files:
        pid = get_product_id(img_file)
        # Dummy name since we lack metadata
        p_name = f"Fashion Item {pid}"
        
        base_price = np.random.randint(500, 5000)
        
        for v in vendors:
            # Vary price slightly per vendor
            price = max(199, base_price + np.random.randint(-200, 200))
            
            price_data.append({
                "product_id": pid,
                "product_name": p_name,
                "vendor": v,
                "price": price,
                "url": f"https://www.{v.lower()}.com/p/{pid}",
                "filename": img_file
            })
            
    df = pd.DataFrame(price_data)
    csv_path = os.path.join(DATA_DIR, "product_prices.csv")
    df.to_csv(csv_path, index=False)
    print(f"Created {csv_path} with {len(df)} entries.")

def main():
    print("=" * 60)
    print("   DATA INDEXER: MobileNetV4 + Fractional Config")
    print("=" * 60)
    
    # 1. Scan Images
    all_files = os.listdir(IMAGES_DIR)
    image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"Found {len(image_files)} images in {IMAGES_DIR}")
    
    if len(image_files) == 0:
        print("[ERROR] No images found! Please add images to 'data/images/' first.")
        return

    # 2. Update Price CSV
    create_price_database(image_files)
    
    # 3. Extract Features
    print("\nInitializing MobileNetV4 Feature Extractor...")
    try:
        fe = FeatureExtractor()
    except Exception as e:
        print(f"[ERROR] Could not initialize feature extractor: {e}")
        return

    data_records = []
    
    print(f"\nExtracting features for {len(image_files)} images...")
    for img_file in tqdm(image_files):
        img_path = os.path.join(IMAGES_DIR, img_file)
        
        try:
            # Extract feature vector
            feat = fe.extract(img_path)
            
            pid = get_product_id(img_file)
            
            data_records.append({
                'product_id': pid,
                'image_path': img_path,
                'features': feat
            })
        except Exception as e:
            print(f"[WARN] Failed to process {img_file}: {e}")
            continue
            
    # 4. Save as DataFrame
    if data_records:
        df_features = pd.DataFrame(data_records)
        save_path = os.path.join(DATA_DIR, "features.pkl")
        
        print(f"\nSaving {len(df_features)} records to {save_path}...")
        df_features.to_pickle(save_path)
        print("[OK] Indexing complete!")
    else:
        print("[WARN] No features extracted.")

if __name__ == "__main__":
    main()
