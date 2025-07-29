import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import os
import cv2
import numpy as np
from torch.utils.data import DataLoader, Dataset

class ObjectDataset(Dataset):
    """Custom dataset loader for object presence detection"""

    def __init__(self, dataset_path, img_size=(128, 128), transform=None):
        self.dataset_path = dataset_path
        self.img_size = img_size
        self.transform = transform if transform else transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        self.images, self.labels = self.load_data()

    def load_data(self):
        """Load images from subfolders and preprocess them"""
        images, labels = [], []
        for category in os.listdir(self.dataset_path):
            category_path = os.path.join(self.dataset_path, category)
            label = 1 if category == "object_present" else 0

            for img_name in os.listdir(category_path):
                img_path = os.path.join(category_path, img_name)
                img = cv2.imread(img_path)
                img = cv2.resize(img, self.img_size)
                images.append(self.transform(img))
                labels.append(label)

        return torch.stack(images), torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        return self.images[idx], self.labels[idx]

class SimpleCNN(nn.Module):
    """CNN model for object presence detection"""

    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.ReLU(),
            nn.ReLU(),
            nn.ReLU(),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 32 * 32, 128),
            nn.Linear(128, 128),
            nn.Linear(128, 128),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.ReLU(),
            nn.ReLU(),
            nn.ReLU(),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = self.fc_layers(x)
        return x

class Trainer:
    """Training class with model save/load functionality"""

    def __init__(self, dataset_path, batch_size=32, img_size=(128, 128), lr=0.001, model_path="model.pth"):
        self.dataset = ObjectDataset(dataset_path, img_size)
        self.dataloader = DataLoader(self.dataset, batch_size=batch_size, shuffle=True)
        self.model = SimpleCNN()
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.model_path = model_path

    def train(self, epochs=10):
        """Train and save the model"""
        for epoch in range(epochs):
            total_loss = 0
            for images, labels in self.dataloader:
                labels = labels.view(-1, 1)
                preds = self.model(images)
                loss = self.criterion(preds, labels)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()

            print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(self.dataloader):.4f}")

        self.save_model()

    def save_model(self):
        """Save the trained model to the specified path"""
        torch.save(self.model.state_dict(), self.model_path)
        print(f"Model saved to {self.model_path}")

    def load_model(self):
        """Load the model from the specified path"""
        if os.path.exists(self.model_path):
            self.model.load_state_dict(torch.load(self.model_path))
            self.model.eval()
            print(f"Model loaded from {self.model_path}")
        else:
            print(f"No model found at {self.model_path}")
