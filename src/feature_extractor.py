import timm
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

class FeatureExtractor:
    def __init__(self):
        # Load MobileNetV4 backbone from timm
        # "mobilenetv4_conv_medium.e500_r256_in1k" is a specific pretrained config
        print(f"[INFO] Loading MobileNetV4 model...")
        try:
            self.model = timm.create_model(
                'mobilenetv4_conv_medium.e500_r256_in1k',
                pretrained=True,
                num_classes=0  # Remove classification head, output features directly
            )
            self.model.eval()  # Set to evaluation mode
            
            # Standard ImageNet preprocessing
            self.preprocess = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], 
                    std=[0.229, 0.224, 0.225]
                ),
            ])
            print("[OK] MobileNetV4 loaded successfully.")
            
        except Exception as e:
            print(f"[ERROR] Failed to load MobileNetV4: {e}")
            raise e

    def extract(self, img):
        """
        Extract features from an image.
        Returns a normalized 1D numpy array.
        """
        # Load image if string path
        if isinstance(img, str):
            img = Image.open(img)
            
        # Ensure RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Preprocess
        img_tensor = self.preprocess(img)
        img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension (1, C, H, W)
        
        # Extract features
        with torch.no_grad():
            features = self.model(img_tensor)
            
        # Convert to numpy and flatten
        features = features.numpy().flatten()
        
        # Normalize (L2) - Good practice for retrieval often, 
        # though fractional distance might behave differently, 
        # usually normalized vectors are safer. 
        # The user didn't STRICTLY say normalize, but implied it by "standard preprocessing".
        # I will keep normalization as it stabilizes distance metrics.
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
            
        return features
