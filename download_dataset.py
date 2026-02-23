"""
Download Fashion Product Images Dataset from Kaggle
Before running, ensure you have:
1. Install kaggle: pip install kaggle
2. Place kaggle.json in C:\\Users\\<username>\\.kaggle\\kaggle.json
"""

import os
import zipfile
import shutil
import pandas as pd
from pathlib import Path

def download_dataset():
    print("[INFO] Downloading Fashion Product Images Dataset from Kaggle...")
    
    # Create data directory
    data_dir = Path("data/fashion-dataset")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Download using Kaggle API
    try:
        import kaggle
        kaggle.api.authenticate()
        
        print("[DOWNLOAD] Downloading dataset (this may take a few minutes)...")
        kaggle.api.dataset_download_files(
            'paramaggarwal/fashion-product-images-small',
            path=str(data_dir),
            unzip=True
        )
        print("[OK] Download complete!")
        
    except Exception as e:
        print(f"[ERROR] Kaggle download failed: {e}")
        print("\n[FIX] Make sure you have:")
        print("   1. kaggle.json in C:\\Users\\<YourUsername>\\.kaggle\\")
        print("   2. Run: pip install kaggle")
        return False
    
    # Organize images by category
    print("\n[INFO] Organizing dataset by categories...")
    organize_dataset(data_dir)
    
    return True

def organize_dataset(data_dir):
    """
    Organize images into category folders for training
    """
    # Check for styles.csv (metadata)
    styles_path = data_dir / "styles.csv"
    images_dir = data_dir / "images"
    organized_dir = data_dir / "organized"
    organized_dir.mkdir(exist_ok=True)
    
    if not styles_path.exists():
        print("[WARN] styles.csv not found. Looking for alternative structure...")
        # Try myntradataset structure
        myntra_path = data_dir / "myntradataset"
        if myntra_path.exists():
            styles_path = myntra_path / "styles.csv"
            images_dir = myntra_path / "images"
    
    if not styles_path.exists():
        print("[ERROR] Could not find styles.csv metadata")
        return
    
    # Load metadata
    try:
        df = pd.read_csv(styles_path, on_bad_lines='skip')
        print(f"[INFO] Found {len(df)} products in metadata")
    except Exception as e:
        print(f"[ERROR] Error reading styles.csv: {e}")
        return
    
    # Get top 20 categories for training
    if 'articleType' in df.columns:
        top_categories = df['articleType'].value_counts().head(20).index.tolist()
        df_filtered = df[df['articleType'].isin(top_categories)]
    elif 'subCategory' in df.columns:
        top_categories = df['subCategory'].value_counts().head(20).index.tolist()
        df_filtered = df[df['subCategory'].isin(top_categories)]
        df_filtered = df_filtered.rename(columns={'subCategory': 'articleType'})
    else:
        print("[ERROR] No category column found")
        return
    
    print(f"[INFO] Organizing images into {len(top_categories)} categories...")
    
    # Create category folders and copy images
    count = 0
    for _, row in df_filtered.iterrows():
        try:
            category = str(row['articleType']).replace('/', '_').replace(' ', '_')
            img_id = str(row['id'])
            
            # Source image path
            src_img = images_dir / f"{img_id}.jpg"
            if not src_img.exists():
                continue
            
            # Create category folder
            cat_dir = organized_dir / category
            cat_dir.mkdir(exist_ok=True)
            
            # Copy image
            dst_img = cat_dir / f"{img_id}.jpg"
            if not dst_img.exists():
                shutil.copy(src_img, dst_img)
                count += 1
                
            if count % 500 == 0:
                print(f"   Processed {count} images...")
                
        except Exception as e:
            continue
    
    print(f"[OK] Organized {count} images into {len(top_categories)} categories!")
    print(f"[INFO] Dataset ready at: {organized_dir}")
    
    # Save category list
    with open(data_dir / "categories.txt", "w") as f:
        for cat in top_categories:
            f.write(f"{cat}\n")
    
    return organized_dir

if __name__ == "__main__":
    success = download_dataset()
    if success:
        print("\n[DONE] Dataset ready! Now run: python train.py")
