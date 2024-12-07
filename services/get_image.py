# services/get_image.py
import os
from io import BytesIO
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from torchvision.models import ResNet50_Weights

from extensions import db
from models import Product
from flask import current_app

def get_images_and_labels():
    data = []
    with current_app.app_context():
        for product in db.session.query(Product).all():
            if product.image:
                image = Image.open(BytesIO(product.image))
                data.append((image, product.name))
            for image_record in product.images:
                image = Image.open(BytesIO(image_record.image))
                data.append((image, image_record.product.name))
    return data

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

class ProductDataset(Dataset):
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform
        self.label_to_int = self.create_label_mapping()

    def create_label_mapping(self):
        labels = set(label for _, label in self.data)
        return {label: idx for idx, label in enumerate(labels)}

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image, label = self.data[idx]
        if self.transform:
            image = self.transform(image)
        label = torch.tensor(self.label_to_int[label], dtype=torch.long)  # Convert label to integer tensor
        return image, label

def train_model():
    # Load the pre-trained model with weights
    model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
    num_features = model.fc.in_features

    # Define the data variable
    data = get_images_and_labels()

    # Define the device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Define the criterion
    criterion = nn.CrossEntropyLoss()

    # Freeze tất cả các lớp
    for param in model.parameters():
        param.requires_grad = False

    # Điều chỉnh lớp cuối
    num_classes = len(set(label for _, label in data))
    model.fc = nn.Linear(num_features, num_classes)  # Cập nhật số lớp
    model.to(device)

    # Fine-tuning với dữ liệu mới
    new_data = get_images_and_labels()  # Lấy lại dữ liệu mới
    new_dataset = ProductDataset(new_data, transform=transform)
    new_loader = DataLoader(new_dataset, batch_size=16, shuffle=True)

    optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)
    for epoch in range(5):  # Ít epoch hơn cho fine-tuning
        model.train()
        total_loss = 0
        for images, labels in new_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Fine-tuning Epoch [{epoch+1}/5], Loss: {total_loss/len(new_loader):.4f}")

    torch.save(model.state_dict(), 'static/models/product_model/product_model.pth')

def model_exists():
    return os.path.exists('static/models/product_model/product_model.pth')