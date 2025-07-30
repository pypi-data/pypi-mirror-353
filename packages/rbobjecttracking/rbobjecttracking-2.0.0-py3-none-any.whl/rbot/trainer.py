import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Dataset, random_split
from PIL import Image

# Enable GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ObjectDataset(Dataset):
    """Loads positive images (object) and negative images (not_objects)."""
    def __init__(self, dataset_path, img_size=(128, 128)):
        self.img_size = img_size
        self.object_images = self.load_paths(os.path.join(dataset_path, "object"))
        self.not_object_images = self.load_paths(os.path.join(dataset_path, "not_objects"))
        self.transform = transforms.Compose([
            transforms.RandomRotation(15),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

    def load_paths(self, folder_path):
        return [
            os.path.join(folder_path, img)
            for img in os.listdir(folder_path)
            if img.lower().endswith(('.jpg', '.png', '.jpeg'))
        ]

    def __len__(self):
        return len(self.object_images) + len(self.not_object_images)

    def __getitem__(self, idx):
        if idx < len(self.object_images):
            img_path = self.object_images[idx]
            label = torch.tensor([1.0, 0.0], dtype=torch.float32)  # Object class
        else:
            img_path = self.not_object_images[idx - len(self.object_images)]
            label = torch.tensor([0.0, 1.0], dtype=torch.float32)  # Not-object class

        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"❌ Image not found: {img_path}")

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, self.img_size)

        # Convert NumPy array to PIL Image
        img = Image.fromarray(img)

        img = self.transform(img)  # Apply torchvision transforms
        return img, label

class EnhancedObjectConfidenceCNN(nn.Module):
    """Improved classifier with additional layers for better feature extraction."""
    def __init__(self, input_size):
        super(EnhancedObjectConfidenceCNN, self).__init__()

        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        feature_map_size = input_size[0] // 8  # Adjusted for deeper network
        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * feature_map_size * feature_map_size, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 2),  # Output
            nn.Softmax(dim=1)  # Sigmoid instead of Softmax
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = self.fc_layers(x)
        return x

class Trainer:
    """Trains the model using positive and negative datasets."""
    def __init__(self, dataset_path, batch_size=32, img_size=(128, 128), lr=0.0001, model_path="classifier.pth", use_cuda=False):
        global device
        if not use_cuda:
            device = torch.device("cpu")
        self.dataset = ObjectDataset(dataset_path, img_size)
        train_len = int(0.8 * len(self.dataset))
        val_len = len(self.dataset) - train_len
        train_ds, val_ds = random_split(self.dataset, [train_len, val_len])

        self.train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
        self.val_loader = DataLoader(val_ds, batch_size=batch_size)
        self.model = EnhancedObjectConfidenceCNN(img_size).to(device)  # Move model to GPU
        self.criterion = nn.CrossEntropyLoss()  # Updated loss function for binary classification
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=5, gamma=0.7)  # Learning rate scheduler
        self.model_path = model_path
        self.best_val_loss = float('inf')  # Initialize best validation loss

    def train(self, epochs=10):
        """Trains the model and saves only when validation loss improves."""
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0
            for images, labels in self.train_loader:
                images, labels = images.to(device), labels.to(device)  # Move data to GPU
                preds = self.model(images)
                loss = self.criterion(preds, labels)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()

            self.scheduler.step()  # Adjust learning rate
            print(f"Epoch {epoch+1}/{epochs} | Training Loss: {total_loss:.4f}")

            # Validation step
            self.model.eval()
            val_loss = 0
            with torch.no_grad():
                for images, labels in self.val_loader:
                    images, labels = images.to(device), labels.to(device)
                    preds = self.model(images)
                    val_loss += self.criterion(preds, labels).item()

            val_loss /= len(self.val_loader)
            print(f"[INFO] Validation Loss: {val_loss:.4f}")

            # Save model if validation loss improves
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                torch.save(self.model.state_dict(), self.model_path)
                print(f"✅ Model saved! New best validation loss: {val_loss:.4f}")
            else:
                print("🔄 No improvement, model not saved.")

if __name__ == "__main__":
    trainer = Trainer("dataset")  # Ensure "dataset/object" and "dataset/not_objects" exist
    trainer.train(epochs=10)
