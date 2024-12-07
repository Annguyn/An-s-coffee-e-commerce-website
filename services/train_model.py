import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision.models import resnet50, ResNet50_Weights
from torchvision import transforms
from PIL import Image
from io import BytesIO
from flask import current_app
from extensions import db
from models import Product

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def create_id_label_mapping():
    with current_app.app_context():
        products = Product.query.all()
        id_to_label = {product.id: idx for idx, product in enumerate(products)}
        label_to_id = {idx: product_id for product_id, idx in id_to_label.items()}
        return id_to_label, label_to_id

def get_images_and_labels(id_to_label):
    data = []
    with current_app.app_context():
        for product in db.session.query(Product).all():
            if product.image:
                image = Image.open(BytesIO(product.image)).convert('RGB')
                label = id_to_label[product.id]
                data.append((image, label))
            for image_record in product.product_images:
                image = Image.open(BytesIO(image_record.image)).convert('RGB')
                label = id_to_label[product.id]
                data.append((image, label))
    return data

class ProductDataset(Dataset):
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image, label = self.data[idx]
        if self.transform:
            image = self.transform(image)
        return image, label

def initialize_data(id_to_label):
    data = get_images_and_labels(id_to_label)
    dataset = ProductDataset(data, transform=transform)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
    return dataloader, len(id_to_label)

def load_model():
    model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
    id_to_label, _ = create_id_label_mapping()
    dataloader, num_classes = initialize_data(id_to_label)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    return model, dataloader

def train_model():
    model, dataloader = load_model()

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    EPOCHS = 10
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {total_loss/len(dataloader):.4f}")

    os.makedirs('static/models/product_model', exist_ok=True)
    torch.save(model.state_dict(), 'static/models/product_model/product_model.pth')

def extract_feature_from_db(image_data, model):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    image = Image.open(BytesIO(image_data)).convert('RGB')
    input_tensor = transform(image).unsqueeze(0).to(device)
    model.eval()
    with torch.no_grad():
        feature_vector = model(input_tensor).squeeze().cpu().numpy()
    return feature_vector

def check_and_train_model():
    model_path = 'static/models/product_image/product_model.pth'
    if not os.path.exists(model_path):
        with current_app.app_context():
            train_model()
    else:
        print("Model already exists. It will be retrained when a new product is added.")