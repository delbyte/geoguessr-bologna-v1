import torch
import torch.nn as nn
import torchvision.models as models

class MobileNetGeolocation(nn.Module):
    def __init__(self, pretrained=True):
        super(MobileNetGeolocation, self).__init__()
        # Load a pretrained MobileNetV2 model
        self.mobilenet = models.mobilenet_v2(pretrained=pretrained)
        
        # Get the number of features of the last layer before classification
        in_features = self.mobilenet.last_channel  # Typically 1280 for MobileNetV2
        
        # Replace the classifier with a new one for regression (2 outputs: latitude and longitude)
        self.mobilenet.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(in_features, 2)
            # Optionally add nn.Sigmoid() if you want to constrain outputs to [0,1]
        )
        
    def forward(self, x):
        return self.mobilenet(x)

# For testing purposes
if __name__ == "__main__":
    model = MobileNetGeolocation(pretrained=True)
    test_input = torch.randn(1, 3, 224, 224)
    output = model(test_input)
    print("Output shape:", output.shape)  # Expected: torch.Size([1, 2])
