"""
Product Category Classifier
Uses the trained model to predict what type of product is in an image.
"""
import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os

class ProductClassifier:
    def __init__(self):
        self.model = None
        self.class_names = []
        self._load_model()
        
    def _load_model(self):
        """Load the trained classification model"""
        model_path = "trained_model.keras"
        class_path = "class_indices.json"
        
        if os.path.exists(model_path) and os.path.exists(class_path):
            print("[INFO] Loading classification model...")
            self.model = tf.keras.models.load_model(model_path)
            
            # Load class names (reverse the dict: index -> name)
            with open(class_path, 'r') as f:
                class_indices = json.load(f)
            # Reverse: {0: 'Backpacks', 1: 'Belts', ...}
            self.class_names = {v: k for k, v in class_indices.items()}
            print(f"[OK] Loaded classifier with {len(self.class_names)} categories")
        else:
            print("[WARN] Classification model not found!")
            
    def predict(self, image):
        """
        Predict the category of a product image.
        
        Args:
            image: PIL Image or path to image
            
        Returns:
            tuple: (category_name, confidence)
        """
        if self.model is None:
            return "Product", 0.0
            
        # Load image if path
        if isinstance(image, str):
            image = Image.open(image)
            
        # Preprocess
        img = image.convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Predict
        predictions = self.model.predict(img_array, verbose=0)
        class_idx = np.argmax(predictions[0])
        confidence = predictions[0][class_idx]
        
        # Get class name (make it human readable)
        class_name = self.class_names.get(class_idx, "Product")
        # Convert underscores to spaces: Casual_Shoes -> Casual Shoes
        class_name = class_name.replace('_', ' ')
        
        return class_name, float(confidence)
    
    def get_search_query(self, image):
        """
        Get a search query for the product.
        Returns a string optimized for e-commerce search.
        """
        category, confidence = self.predict(image)
        
        # If confidence is high, use the category directly
        if confidence > 0.5:
            return category
        else:
            # Add generic term if uncertain
            return f"{category} fashion"


# Test
if __name__ == "__main__":
    classifier = ProductClassifier()
    # Test with a sample image
    test_images = [
        "data/images",
    ]
    import os
    img_dir = "data/images"
    if os.path.exists(img_dir):
        sample = os.listdir(img_dir)[:3]
        for img_name in sample:
            img_path = os.path.join(img_dir, img_name)
            category, conf = classifier.predict(img_path)
            print(f"{img_name}: {category} ({conf:.1%})")
