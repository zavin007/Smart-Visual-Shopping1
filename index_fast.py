"""
FAST Batch Indexer - Optimized for CPU
Uses batch processing (32 images at once) for ~3-4x speedup
"""
import os
import shutil
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from tqdm import tqdm
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# Paths
BASE_DIR = Path.cwd()
SOURCE_DIR = BASE_DIR / "data" / "fashion-dataset" / "organized"
DEST_DIR = BASE_DIR / "data" / "images"
DATA_DIR = BASE_DIR / "data"

BATCH_SIZE = 32  # Process 32 images at once
IMG_SIZE = (224, 224)

def get_product_id(filename):
    stem = os.path.splitext(filename)[0]
    try:
        pid = int(stem.split('_')[0])
    except:
        pid = abs(hash(stem)) % 100000
    return pid

def load_and_preprocess(img_path):
    """Load and preprocess a single image"""
    try:
        img = Image.open(img_path).convert('RGB')
        img = img.resize(IMG_SIZE)
        arr = np.array(img)
        return preprocess_input(arr)
    except:
        return None

def main():
    print("=" * 60)
    print("   FAST BATCH INDEXER - Optimized for Speed")
    print("=" * 60)
    
    # Load model once
    print("\n[Loading Model...]")
    try:
        full_model = tf.keras.models.load_model("trained_model.keras")
        # Find the 256-dim layer
        layer_name = None
        for layer in full_model.layers[-5:]:
            if isinstance(layer, tf.keras.layers.Dense) and layer.units == 256:
                layer_name = layer.name
                break
        if layer_name:
            model = tf.keras.Model(inputs=full_model.input, outputs=full_model.get_layer(layer_name).output)
            print(f"[OK] Using fine-tuned model, layer: {layer_name}")
        else:
            for layer in full_model.layers:
                if isinstance(layer, tf.keras.layers.GlobalAveragePooling2D):
                    model = tf.keras.Model(inputs=full_model.input, outputs=layer.output)
                    break
            print("[OK] Using GlobalAveragePooling layer")
    except Exception as e:
        print(f"[WARN] Could not load trained model: {e}")
        print("[INFO] Using default MobileNetV2...")
        base = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
        model = tf.keras.Model(inputs=base.input, outputs=x)
    
    # 1. Clean & Copy
    print("\n[Step 1/3] Preparing store...")
    if DEST_DIR.exists():
        for f in DEST_DIR.glob("*"):
            try: os.remove(f)
            except: pass
    else:
        DEST_DIR.mkdir(parents=True)
    
    all_images = list(SOURCE_DIR.rglob("*.jpg"))
    print(f"   Found {len(all_images)} images. Copying...")
    
    for src in tqdm(all_images, desc="Copying", ncols=80):
        try:
            shutil.copy2(src, DEST_DIR / src.name)
        except:
            pass
    
    # 2. Generate Price DB
    print("\n[Step 2/3] Building price database...")
    image_files = sorted([f for f in os.listdir(DEST_DIR) if f.endswith('.jpg')])
    
    price_data = []
    vendors = ["Amazon", "Flipkart", "Myntra"]
    for img_file in image_files:
        pid = get_product_id(img_file)
        base_price = np.random.randint(500, 5000)
        for v in vendors:
            price = max(199, base_price + np.random.randint(-200, 200))
            price_data.append({
                "product_id": pid,
                "product_name": f"Fashion Item {pid}",
                "vendor": v,
                "price": price,
                "url": f"https://www.{v.lower()}.com/p/{pid}",
                "filename": img_file
            })
    
    pd.DataFrame(price_data).to_csv(DATA_DIR / "product_prices.csv", index=False)
    print(f"   Created {len(price_data)} price entries.")
    
    # 3. Batch Feature Extraction (THE FAST PART)
    print(f"\n[Step 3/3] Extracting features (Batch Size: {BATCH_SIZE})...")
    
    features = []
    img_paths = []
    ids = []
    
    # Process in batches
    num_batches = (len(image_files) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for batch_idx in tqdm(range(num_batches), desc="Features", ncols=80):
        start = batch_idx * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(image_files))
        batch_files = image_files[start:end]
        
        # Load batch of images
        batch_images = []
        batch_paths = []
        batch_ids = []
        
        for img_file in batch_files:
            img_path = DEST_DIR / img_file
            img_arr = load_and_preprocess(img_path)
            if img_arr is not None:
                batch_images.append(img_arr)
                batch_paths.append(str(img_path))
                batch_ids.append(get_product_id(img_file))
        
        if batch_images:
            # Batch predict (MUCH faster than single predictions)
            batch_arr = np.array(batch_images)
            batch_features = model.predict(batch_arr, verbose=0)
            
            # Normalize
            norms = np.linalg.norm(batch_features, axis=1, keepdims=True)
            batch_features = batch_features / (norms + 1e-10)
            
            features.extend(batch_features)
            img_paths.extend(batch_paths)
            ids.extend(batch_ids)
    
    # Save
    features = np.array(features)
    pickle.dump(features, open(DATA_DIR / "features.pkl", "wb"))
    pickle.dump(ids, open(DATA_DIR / "ids.pkl", "wb"))
    pickle.dump(img_paths, open(DATA_DIR / "img_paths.pkl", "wb"))
    
    print("\n" + "=" * 60)
    print(f"   DONE! Indexed {len(features)} products.")
    print("   Now restart your app: streamlit run app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
