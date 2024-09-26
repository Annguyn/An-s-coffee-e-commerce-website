from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_required, current_user
from models import db, favourite, Product, CartItem, ShoppingSession
from extensions import db
from flask_login import current_user
from datetime import datetime

billing_information_bp = Blueprint('billing_information', __name__)

@billing_information_bp.route('/billing_information', methods=['GET'])
def show_billing_information():
    session = ShoppingSession.query.filter_by(user_id=current_user.id).first()
    cart_items = CartItem.query.filter_by(session_id=session.id).all()
    products = {}
    for item in cart_items:
        product = Product.query.get(item.product_id)
        products[item.product_id] = product
    return render_template('billing-information.html', user=current_user, cart_items=cart_items, session=session, products=products)