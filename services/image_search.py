import logging
import torch
from flask import current_app
from torch import nn
from torchvision.models import resnet50
from torchvision import transforms
from PIL import Image
from io import BytesIO

from models import Product
from app import app

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_id_label_mapping():
    with app.app_context():
        products = Product.query.all()
        id_to_label = {product.id: idx for idx, product in enumerate(products)}
        label_to_id = {idx: product_id for product_id, idx in id_to_label.items()}
        return id_to_label, label_to_id

def get_num_classes():
    with app.app_context():
        return Product.query.count()

model = resnet50(pretrained=False)
with app.app_context():
    model.fc = nn.Linear(model.fc.in_features, get_num_classes())
model.load_state_dict(torch.load('static/models/product_model/product_model.pth'))
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def predict_product(image_file):
    logger.debug("predict_product function called")
    _, label_to_id = create_id_label_mapping()
    image = Image.open(BytesIO(image_file.read())).convert('RGB')
    input_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
    _, predicted = torch.max(output, 1)
    predicted_label = predicted.item()
    predicted_product_id = label_to_id[predicted_label]
    logger.debug(f"Predicted class index: {predicted_label}")

    with app.app_context():
        product = Product.query.get(predicted_product_id)
        product_name = product.name if product else "Unknown"
        logger.debug(f"Predicted product name: {product_name}")
        return product_name