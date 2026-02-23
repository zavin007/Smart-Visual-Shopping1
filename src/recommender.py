import numpy as np
import pandas as pd
import os
import pickle

class Recommender:
    def __init__(self, data_dir="data"):
        features_path = os.path.join(data_dir, "features.pkl")
        
        if os.path.exists(features_path):
            # Load the DataFrame created by create_data.py
            print(f"[INFO] Loading features from {features_path}...")
            self.df = pd.read_pickle(features_path)
            
            # Convert features column to a proper numpy matrix for fast vectorization
            # self.df['features'] contains numpy arrays. We stack them.
            self.feature_matrix = np.stack(self.df['features'].values)
            print(f"[OK] Loaded index with {len(self.df)} items. Matrix shape: {self.feature_matrix.shape}")
        else:
            raise FileNotFoundError(f"Features file not found at {features_path}")

    def fractional_distance(self, query_vector, epsilon=1e-10):
        """
        Calculate Fractional Distance Metric:
        Sum(|x - y|^0.3)^(1/0.3)
        """
        # Broadcasting: (N, D) - (D,) -> (N, D)
        diff = np.abs(self.feature_matrix - query_vector)
        
        # Add epsilon to avoid instability with 0 values raised to fractional power (though 0.3 is pos)
        # Power 0.3
        pow_diff = np.power(diff + epsilon, 0.3)
        
        # Sum across dimensions
        sum_pow = np.sum(pow_diff, axis=1)
        
        # Root (1/0.3)
        dist = np.power(sum_pow, 1/0.3)
        
        return dist

    def find_similar(self, query_feature):
        """
        Find closest match using Fractional Distance.
        Returns: (product_id, image_path_of_match, distance)
        """
        # Calculate distances to all items
        distances = self.fractional_distance(query_feature)
        
        # Find index of minimum distance
        min_idx = np.argmin(distances)
        min_dist = distances[min_idx]
        
        # Get data from DataFrame
        best_match = self.df.iloc[min_idx]
        
        return best_match['product_id'], best_match['image_path'], float(min_dist)
