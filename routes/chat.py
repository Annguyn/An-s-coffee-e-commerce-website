import logging
from flask import Blueprint, request, jsonify
from models import db, Product
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import PhobertTokenizer, AutoModelForSequenceClassification

logging.basicConfig(level=logging.DEBUG)

chat_bp = Blueprint('chat', __name__)

model_path_eng = "static/models/intent_model"
tokenizer_eng = BertTokenizer.from_pretrained(model_path_eng)
model_eng = BertForSequenceClassification.from_pretrained(model_path_eng)

model_path_vn = "static/models/intent_model_vn"
tokenizer_vn = PhobertTokenizer.from_pretrained(model_path_vn)
model_vn = AutoModelForSequenceClassification.from_pretrained(model_path_vn)

model_eng.eval()
model_vn.eval()

id_to_label_eng = {0: "price inquiry", 1: "price range inquiry", 2: "greeting", 3: "description"}
id_to_label_vn = {0: "price range inquiry", 1: "price inquiry", 2: "greeting", 3: "description"}

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    min_price = data.get('min_price')
    max_price = data.get('max_price')
    language = data.get('language', 'ENG')

    logging.debug(f"Received message: {user_message}")
    logging.debug(f"Language: {language}")

    if language == 'VN':
        tokenizer = tokenizer_vn
        model = model_vn
        id_to_label = id_to_label_vn
        default_reply = "Tôi ở đây để giúp bạn với các câu hỏi về sản phẩm!"
        greeting_reply = "Xin chào! Tôi có thể giúp gì cho bạn hôm nay?"
        description_reply = "Vui lòng cung cấp tên sản phẩm."
        price_inquiry_reply = "Vui lòng cung cấp tên sản phẩm."
        price_range_inquiry_reply = "Vui lòng cung cấp cả giá tối thiểu và tối đa."
    else:
        tokenizer = tokenizer_eng
        model = model_eng
        id_to_label = id_to_label_eng
        default_reply = "I'm here to help with product inquiries!"
        greeting_reply = "Hello! How can I help you today?"
        description_reply = "Please provide a product name."
        price_inquiry_reply = "Please provide a product name."
        price_range_inquiry_reply = "Please provide both min and max price."

    logging.debug(f"Using tokenizer: {tokenizer}")
    logging.debug(f"Using model: {model}")

    if min_price and max_price:
        intent = "price range inquiry"
    else:
        inputs = tokenizer(user_message, return_tensors="pt", truncation=True, padding=True, max_length=128)
        logging.debug(f"Tokenized inputs: {inputs}")

        with torch.no_grad():
            outputs = model(**inputs)
            predicted_class = torch.argmax(outputs.logits, dim=1).item()
            intent = id_to_label.get(predicted_class, "unknown")

    logging.debug(f"Determined intent: {intent}")

    bot_reply = default_reply

    if intent == "greeting":
        bot_reply = greeting_reply
    elif intent == "description":
        if user_message.split():
            product_name = user_message.split()[-1]
            product = Product.query.filter(Product.name.ilike(f"%{product_name}%")).first()
            if product:
                bot_reply = f"The product {product.name} is described as: {product.desc}." if language == 'ENG' else f"Sản phẩm {product.name} được mô tả như sau: {product.desc}."
            else:
                bot_reply = "Sorry, I couldn't find that product." if language == 'ENG' else "Xin lỗi, tôi không tìm thấy sản phẩm đó."
        else:
            bot_reply = description_reply
    elif intent == "price inquiry":
        if user_message.split():
            product_name = user_message.split()[-1]
            product = Product.query.filter(Product.name.ilike(f"%{product_name}%")).first()
            if product:
                bot_reply = f"The price of {product.name} is {product.price}." if language == 'ENG' else f"Giá của {product.name} là {product.price}."
            else:
                bot_reply = "Sorry, I couldn't find that product's price." if language == 'ENG' else "Xin lỗi, tôi không tìm thấy giá của sản phẩm đó."
        else:
            bot_reply = price_inquiry_reply
    elif intent == "price range inquiry":
        if min_price is not None and max_price is not None:
            products = Product.query.filter(Product.price.between(min_price, max_price)).all()
            if products:
                bot_reply = "Products in your price range:\n" + "\n".join([f"{p.name} costs {p.price}" for p in products]) if language == 'ENG' else "Các sản phẩm trong khoảng giá của bạn:\n" + "\n".join([f"{p.name} có giá {p.price}" for p in products])
            else:
                bot_reply = "Sorry, no products found in that range." if language == 'ENG' else "Xin lỗi, không tìm thấy sản phẩm nào trong khoảng giá đó."
        else:
            bot_reply = price_range_inquiry_reply

    logging.debug(f"Bot reply: {bot_reply}")

    return jsonify({'reply': bot_reply, 'intent': intent})



