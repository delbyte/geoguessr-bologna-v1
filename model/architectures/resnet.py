import torch
import torch.nn as nn
import torchvision.models as models

class ResNetGeolocation(nn.Module):
    def __init__(self, pretrained=True):
        super(ResNetGeolocation, self).__init__()
        self.resnet = models.resnet18(pretrained=pretrained)
        
        # Modify the final fully connected layer to output 2 values (latitude, longitude)
        in_features = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(in_features, 2)
    
    def forward(self, x):
        return self.resnet(x)

# Model initialization for testing
if __name__ == "__main__":
    model = ResNetGeolocation(pretrained=True)
    test_input = torch.randn(1, 3, 224, 224)
    output = model(test_input)
    print("Output Shape:", output.shape)  # Expected: torch.Size([1, 2])
