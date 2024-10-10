from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import csrf
from models import ShoppingSession, CartItem, OrderDetails, OrderItems, PaymentDetails
from models.favourite import Favourite
from models.product import Product, ProductCategory, ProductInventory
from flask_login import current_user, login_required
from routes.cart import show_cart

order_bp = Blueprint('order', __name__)
@order_bp.route('/order')
@login_required
def show_order():
    user = current_user
    orders = OrderDetails.query.filter_by(user_id=user.id).join(PaymentDetails).filter(PaymentDetails.status == "success").all()
    categories= ProductCategory.query.all()
    orders_with_items = []

    for order in orders:
        order_items = OrderItems.query.filter_by(order_id=order.id).all()
        orders_with_items.append({
            'order': order,
            'items': order_items,
            'created_at': order.created_at.isoformat()
        })

    return render_template('order.html', user=user,
                           orders_with_items=orders_with_items, categories=categories)