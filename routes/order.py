from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from extensions import csrf, db
from models import ShoppingSession, CartItem, OrderDetails, OrderItems, PaymentDetails
from models.favourite import Favourite
from models.product import Product, ProductCategory, ProductInventory, Comment
from flask_login import current_user, login_required
from routes.cart import show_cart

order_bp = Blueprint('order', __name__)
from sqlalchemy import func

@order_bp.route('/order')
@login_required
def show_order():
    user = current_user
    status_filter = request.args.get('status')
    page = request.args.get('page', 1, type=int)

    if status_filter:
        orders_query = OrderDetails.query.filter_by(user_id=user.id, status=status_filter)
    else:
        orders_query = OrderDetails.query.filter_by(user_id=user.id)

    orders_paginated = orders_query.order_by(OrderDetails.created_at.desc()).paginate(page=page, per_page=3)
    categories = ProductCategory.query.all()
    orders_with_items = []

    for order in orders_paginated.items:
        order_items = OrderItems.query.filter_by(order_id=order.id).all()
        items_with_ratings = []
        for item in order_items:
            avg_rating = db.session.query(func.avg(Comment.rating)).filter(Comment.product_id == item.product_id).scalar()
            items_with_ratings.append({
                'item': item,
                'avg_rating': avg_rating
            })
        orders_with_items.append({
            'order': order,
            'items': items_with_ratings,
            'created_at': order.created_at.isoformat()
        })

    return render_template('order.html', user=user,
                           orders_with_items=orders_with_items, categories=categories, pagination=orders_paginated)
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
    return redirect(url_for('order.show_order'))
