import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import cv2
import os
import numpy as np

# Custom Dataset Class
class GeolocationDataset(Dataset):
    def __init__(self, csv_file, transform=None):
        self.data = pd.read_csv(csv_file)
        self.transform = transform
        
        # Normalize lat/lon to be between 0 and 1 for better training stability
        self.lat_min, self.lat_max = self.data['latitude'].min(), self.data['latitude'].max()
        self.lon_min, self.lon_max = self.data['longitude'].min(), self.data['longitude'].max()
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        img_path = self.data.iloc[idx, 0]  # Image path
        lat = self.data.iloc[idx, 1]       # Latitude
        lon = self.data.iloc[idx, 2]       # Longitude
        
        # Read Image (OpenCV loads in BGR format)
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB
        image = cv2.resize(image, (224, 224))  # Resize to match model input
        
        # Normalize Latitude & Longitude
        lat = (lat - self.lat_min) / (self.lat_max - self.lat_min)
        lon = (lon - self.lon_min) / (self.lon_max - self.lon_min)
        target = torch.tensor([lat, lon], dtype=torch.float32)
        
        # Apply Transformations
        if self.transform:
            image = self.transform(image)
        
        return image, target

# Data Augmentation & Normalization
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.RandomApply([transforms.ColorJitter(brightness=0.2, contrast=0.2)], p=0.5),
    transforms.RandomApply([transforms.GaussianBlur(kernel_size=(5, 5), sigma=(0.1, 2.0))], p=0.3),
    transforms.RandomRotation(degrees=15),
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load Dataset
csv_path = "dataset/finaldata.csv" 
dataset = GeolocationDataset(csv_file=csv_path, transform=transform)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True, num_workers=0)

# Check if it loads correctly
sample_image, sample_target = next(iter(dataloader))
print(f"Image Tensor Shape: {sample_image.shape}, Target: {sample_target[:5]}")
