import torch
import torch.nn as nn
import timm
import numpy as np

class SiameseNetwork(nn.Module):
    """
    Siamese Network Architecture using MobileNetV4 Backbone.
    
    Structure:
    Input 1 --> [MobileNetV4] --> Vector 1
                                     |
                                [Distance]
                                     |
    Input 2 --> [MobileNetV4] --> Vector 2
    
    Key Feature: The MobileNetV4 weights are SHARED between both branches.
    """
    def __init__(self, model_name='mobilenetv4_conv_medium.e500_r256_in1k', pretrained=True):
        super(SiameseNetwork, self).__init__()
        
        # Load the backbone (Shared Weights)
        print(f"[SIAMESE] Initializing Shared Backbone: {model_name}")
        self.backbone = timm.create_model(
            model_name,
            pretrained=pretrained,
            num_classes=0  # Return features, not classes
        )
        self.backbone.eval() # Inference mode by default

    def forward_one(self, x):
        """Pass one image through the backbone"""
        return self.backbone(x)

    def forward(self, input1, input2):
        """
        Pass pair of images through the same backbone.
        Returns the two feature vectors.
        """
        output1 = self.forward_one(input1)
        output2 = self.forward_one(input2)
        return output1, output2

    def calculate_distance(self, v1, v2):
        """
        Compute Fractional Distance (Research Paper Metric)
        d(x,y) = sum(|x-y|^0.3)^(1/0.3)
        """
        # Ensure numpy
        if isinstance(v1, torch.Tensor): v1 = v1.detach().cpu().numpy()
        if isinstance(v2, torch.Tensor): v2 = v2.detach().cpu().numpy()
        
        diff = np.abs(v1 - v2)
        pow_diff = np.power(diff + 1e-10, 0.3)
        dist = np.power(np.sum(pow_diff), 1/0.3)
        return dist
