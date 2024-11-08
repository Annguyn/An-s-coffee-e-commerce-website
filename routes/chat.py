from flask import Blueprint, request, jsonify
from models import db, Product
import torch
from transformers import BertTokenizer, BertForSequenceClassification

chat_bp = Blueprint('chat', __name__)

model_path = "static/models/intent_model"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)

model.eval()

id_to_label = {0: "price inquiry", 1: "price range inquiry", 2: "greeting", 3: "description"}

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    min_price = data.get('min_price')
    max_price = data.get('max_price')

    if min_price and max_price:
        intent = "price range inquiry"
    else:
        inputs = tokenizer(user_message, return_tensors="pt", truncation=True, padding=True, max_length=128)

        with torch.no_grad():
            outputs = model(**inputs)
            predicted_class = torch.argmax(outputs.logits, dim=1).item()
            intent = id_to_label.get(predicted_class, "unknown")

    bot_reply = "I'm here to help with product inquiries!"

    if intent == "greeting":
        bot_reply = "Hello! How can I help you today?"

    elif intent == "description":
        if user_message.split():
            product_name = user_message.split()[-1]
            product = Product.query.filter(Product.name.ilike(f"%{product_name}%")).first()
            if product:
                bot_reply = f"The product {product.name} is described as: {product.desc}."
            else:
                bot_reply = "Sorry, I couldn't find that product."
        else:
            bot_reply = "Please provide a product name."

    elif intent == "price inquiry":
        if user_message.split():
            product_name = user_message.split()[-1]
            product = Product.query.filter(Product.name.ilike(f"%{product_name}%")).first()
            if product:
                bot_reply = f"The price of {product.name} is {product.price}."
            else:
                bot_reply = "Sorry, I couldn't find that product's price."
        else:
            bot_reply = "Please provide a product name."

    elif intent == "price range inquiry":
        if min_price is not None and max_price is not None:
            products = Product.query.filter(Product.price.between(min_price, max_price)).all()
            if products:
                bot_reply = "Products in your price range:\n" + "\n".join([f"{p.name} costs {p.price}" for p in products])
            else:
                bot_reply = "Sorry, no products found in that range."
        else:
            bot_reply = "Please provide both min and max price."

    return jsonify({'reply': bot_reply, 'intent': intent})
