import os
import shutil
import random
from pathlib import Path
import sys

# Paths
BASE_DIR = Path.cwd()
SOURCE_DIR = BASE_DIR / "data" / "fashion-dataset" / "organized"
DEST_DIR = BASE_DIR / "data" / "images"
NUM_IMAGES = 100

def fix():
    print(f"[INFO] Fixing Data Store...")
    print(f"[INFO] Source: {SOURCE_DIR}")
    print(f"[INFO] Dest: {DEST_DIR}")

    if not SOURCE_DIR.exists():
        print("[ERROR] Source dataset not found!")
        return

    # 1. Clean Destination
    if DEST_DIR.exists():
        print("[INFO] Removing old dummy images...")
        try:
            # Try removing files individually
            for f in DEST_DIR.glob("*"):
                try: 
                    os.remove(f) 
                except Exception as e:
                    print(f"[WARN] Failed to delete {f.name}: {e}")
        except Exception as e:
            print(f"[ERROR] ensuring clean directory: {e}")
    else:
        DEST_DIR.mkdir(parents=True)

    # 2. Gather Real Images
    print("[INFO] Scanning for real products...")
    all_images = list(SOURCE_DIR.rglob("*.jpg"))
    print(f"[INFO] Found {len(all_images)} total images.")

    if not all_images:
        print("[ERROR] No images found. Cannot populate.")
        return

    # 3. Copy Sample
    selection = random.sample(all_images, min(len(all_images), NUM_IMAGES))
    print(f"[INFO] Selecting {len(selection)} items for the store...")
    
    copied = 0
    for src in selection:
        try:
            dst = DEST_DIR / src.name
            shutil.copy2(src, dst)
            copied += 1
        except Exception as e:
            print(f"[WARN] Copy failed for {src.name}: {e}")

    print(f"[SUCCESS] Stocked {copied} items.")

    # 4. Trigger Indexing
    print("[INFO] Re-indexing database (Price & Visuals)...")
    # Execute create_data.py as a subprocess to ensure clean state
    os.system(f"{sys.executable} create_data.py")

if __name__ == "__main__":
    fix()
