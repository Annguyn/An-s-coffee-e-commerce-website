from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from extensions import csrf, db
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
    successful_payments = PaymentDetails.query.all()
    successful_payment_ids = [payment.id for payment in successful_payments]
    orders = OrderDetails.query.filter(OrderDetails.payment_id.in_(successful_payment_ids)).all()
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

@order_bp.route('/order/update_status/<int:order_id>', methods=['POST'])
@login_required
def update_status(order_id):
    action = request.form.get('action')
    order = OrderDetails.query.get_or_404(order_id)

    if order.status == 'Finished':
        if action == 'view_order_items':
            pass
        else:
            flash('This order is already finished and cannot be modified.', 'danger')
            return redirect(url_for('admin.admin_orders'))
    else:
        if action == 'ready_to_delivery':
            order.status = 'Delivery'
        elif action == 'finish':
            order.status = 'Finished'

    db.session.commit()
    flash('Order status updated successfully', 'success')
    return redirect(url_for('admin.admin_orders'))

import base64

@order_bp.route('/order/items/<int:order_id>', methods=['GET'])
@login_required
def get_order_items(order_id):
    order_items = OrderItems.query.filter_by(order_id=order_id).all()
    items = []
    for item in order_items:
        try:
            if isinstance(item.product.image, bytes):
                image_url = f"data:image/png;base64,{base64.b64encode(item.product.image).decode('utf-8')}"
            else:
                image_url = item.product.image
        except UnicodeDecodeError:
            image_url = 'default_image_url'
        items.append({
            'image_url': image_url,
            'title': item.product.name,
            'quantity': item.quantity,
            'price': float(item.product.price)
        })
    return jsonify({'items': items})


@order_bp.route('/order/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = OrderDetails.query.get_or_404(order_id)
    order.status = 'Cancelled'
    db.session.commit()
    flash('Order cancelled successfully', 'success')
