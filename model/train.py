import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from model.architectures.resnet import ResNetGeolocation
from model.architectures.mobilenet import MobileNetGeolocation
from model.utils.dataloader import GeolocationDataset, transform
import os

# Configurations
CSV_PATH = "dataset/finaldata.csv"  # Update if needed
BATCH_SIZE = 16
NUM_EPOCHS = 20
LEARNING_RATE = 0.001
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_TYPE = "resnet"  # change to "mobilenet" to switch models

# Load Dataset
dataset = GeolocationDataset(csv_file=CSV_PATH, transform=transform)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)

# Select Model
if MODEL_TYPE == "resnet":
    model = ResNetGeolocation().to(DEVICE)
elif MODEL_TYPE == "mobilenet":
    model = MobileNetGeolocation().to(DEVICE)
else:
    raise ValueError("Invalid MODEL_TYPE. Choose 'resnet' or 'mobilenet'.")

# Loss and Optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# Training Loop
for epoch in range(NUM_EPOCHS):
    model.train()
    running_loss = 0.0
    
    for images, targets in dataloader:
        images, targets = images.to(DEVICE), targets.to(DEVICE)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
    
    print(f"Epoch [{epoch+1}/{NUM_EPOCHS}], Loss: {running_loss/len(dataloader):.4f}")
    
    # Save model checkpoint
    if (epoch + 1) % 5 == 0:
        model_path = f"model/checkpoints/{MODEL_TYPE}_epoch{epoch+1}.pth"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        torch.save(model.state_dict(), model_path)
        print(f"Checkpoint saved: {model_path}")

print("Training complete!")
