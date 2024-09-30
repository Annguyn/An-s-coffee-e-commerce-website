from flask import Blueprint, request, jsonify
from models import db, Product, CartItem, ShoppingSession
from extensions import db
from flask_login import current_user
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    if "hello" in user_message.lower():
        bot_reply = "Hello! How can I help you today?"
    elif "help" in user_message.lower():
        bot_reply = (
            "Here are some commands you can use:\n"
            "- 'hello': Greet the bot\n"
            "- 'description [product name]': Get the description of a product\n"
            "- 'i have money in range [min_price] to [max_price]': Find products within a price range\n"
            "- 'product [product name]': Get the price and stock information of a product\n"
        )
    elif "description" in user_message.lower():
        product_name = user_message.split("description")[-1].strip()
        product = Product.query.filter(Product.name.ilike(f"%{product_name}%")).first()
        if product:
            bot_reply = f"The product {product.name} is described as: {product.desc}."
        else:
            bot_reply = "Sorry, I couldn't find that product."
    elif "i have money in range" in user_message.lower():
        try:
            price_range = user_message.split("range")[-1].strip().split("to")
            min_price = float(price_range[0].strip())
            max_price = float(price_range[1].strip())
            products = Product.query.filter(Product.price.between(min_price, max_price)).all()
            if products:
                bot_reply = "Here are some products in your price range:\n" + "\n".join([f"{product.name} costs {product.price} --->" for product in products])
            else:
                bot_reply = "Sorry, I couldn't find any products in that price range."
        except (IndexError, ValueError):
            bot_reply = "Please provide a valid price range in the format 'range min_price to max_price'."
    elif "product" in user_message.lower():
        product_name = user_message.split("product")[-1].strip()
        product = Product.query.filter(Product.name.ilike(f"%{product_name}%")).first()
        if product:
            bot_reply = f"The product {product.name} costs {product.price} and we have {product.inventory.quantity} in stock."
        else:
            bot_reply = "Sorry, I couldn't find that product."
    else:
        bot_reply = "Sorry, I can only help with product information."

    return jsonify({ 'reply': bot_reply })