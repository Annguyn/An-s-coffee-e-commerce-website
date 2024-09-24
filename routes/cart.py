from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from models import db, Product
from models.cart import CartItem, ShoppingSession
from extensions import db
from datetime import datetime

add_to_cart_bp = Blueprint('add_to_cart', __name__)

@add_to_cart_bp.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', 1)

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    session = ShoppingSession.query.filter_by(user_id=current_user.id).first()

    if not session:
        session = ShoppingSession(user_id=current_user.id, total=0,created_at=datetime.now(),modified_at=datetime.now())
        db.session.add(session)
        db.session.commit()

    cart_item = CartItem.query.filter_by(session_id=session.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += int(quantity)
        cart_item.modified_at = datetime
    else:
        cart_item = CartItem(session_id=session.id, product_id=product_id, quantity=quantity, created_at=datetime.now(), modified_at=datetime.now())
        db.session.add(cart_item)

    session.total += product.price * int(quantity)
    db.session.commit()

    return jsonify({'message': 'Product added to cart'}), 200