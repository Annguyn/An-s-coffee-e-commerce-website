from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_required, current_user
from models import db, Product
from models.cart import CartItem, ShoppingSession
from extensions import db
from datetime import datetime

from models.coupon import Coupon

add_to_cart_bp = Blueprint('add_to_cart', __name__)
@add_to_cart_bp.route('/cart', methods=['GET', 'POST'])
@login_required
def show_cart():
    shopping_session = ShoppingSession.query.filter_by(user_id=current_user.id).first()
    total_discount = 0

    if shopping_session:
        cart_items = CartItem.query.filter_by(session_id=shopping_session.id).all()
        products = {item.product_id: Product.query.get(item.product_id) for item in cart_items}

        if request.method == 'POST':
            for item in cart_items:
                quantity = int(request.form.get(f'quantity_{item.product_id}', item.quantity))
                product = products[item.product_id]

                if quantity > product.inventory.quantity:
                    return jsonify({'error': f'Insufficient stock for product {product.name}'}), 400
                item.quantity = quantity
                item.modified_at = datetime.now()
                db.session.commit()
            coupon_code = request.form.get('coupon_code')
            if coupon_code:
                applied_coupons = shopping_session.applied_coupons.split(',') if shopping_session.applied_coupons else []
                if coupon_code in applied_coupons:
                    return jsonify({'error': 'Coupon already applied'}), 400

                coupon = Coupon.query.filter_by(code=coupon_code).first()
                if coupon and coupon.start_time <= datetime.now() <= coupon.end_time:
                    if shopping_session.total >= coupon.min_payment:
                        discount = (coupon.percent / 100) * shopping_session.total
                        if discount > coupon.max:
                            discount = coupon.max
                        shopping_session.total -= discount
                        total_discount += discount
                        applied_coupons.append(coupon_code)
                        shopping_session.applied_coupons = ','.join(applied_coupons)
                        db.session.commit()
                    else:
                        return jsonify({'error': 'Minimum payment not met for this coupon'}), 400
                else:
                    return jsonify({'error': 'Invalid or expired coupon code'}), 400

        return render_template('cart.html', user=current_user, cart_items=cart_items,
                               session=shopping_session, products=products, total_discount=total_discount)
    return render_template('cart.html', user=current_user, session=shopping_session, total_discount=total_discount)
@add_to_cart_bp.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity',1))
    print(quantity)
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if product.ProductInventory.quantity < quantity:
        return jsonify({'error': 'Insufficient stock available'}), 400

    session = ShoppingSession.query.filter_by(user_id=current_user.id).first()

    if not session:
        session = ShoppingSession(user_id=current_user.id, total=0, total_before_discount=0, created_at=datetime.now(), modified_at=datetime.now())
        db.session.add(session)
        db.session.commit()

    cart_item = CartItem.query.filter_by(session_id=session.id, product_id=product_id).first()
    if cart_item:
        if product.ProductInventory.quantity < cart_item.quantity + quantity:
            return jsonify({'error': 'Insufficient stock available'}), 400
        cart_item.quantity += quantity
        cart_item.modified_at = datetime.now()
    else:
        cart_item = CartItem(session_id=session.id, product_id=product_id, quantity=quantity, created_at=datetime.now(), modified_at=datetime.now())
        db.session.add(cart_item)

    session.total_before_discount += product.price * quantity
    session.applied_coupons = None
    session.total = session.total_before_discount
    session.modified_at = datetime.now()
    db.session.commit()

    return jsonify({'message': 'Product added to cart'}), 200


@add_to_cart_bp.route('/delete_from_cart', methods=['POST'])
@login_required
def delete_from_cart():
    product_id = request.form.get('product_id')

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    session = ShoppingSession.query.filter_by(user_id=current_user.id).first()
    if not session:
        return jsonify({'error': 'No active shopping session found'}), 404

    cart_item = CartItem.query.filter_by(session_id=session.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'error': 'Product not found in cart'}), 404

    session.total_before_discount = max(0, session.total_before_discount - cart_item.product.price * cart_item.quantity)
    session.total = session.total_before_discount
    session.applied_coupons = None
    session.modified_at = datetime.now()

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({'message': 'Product removed from cart'}), 200


@add_to_cart_bp.route('/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    if product.inventory.quantity < quantity:
        return jsonify({'error': 'Insufficient stock available'}), 400

    session = ShoppingSession.query.filter_by(user_id=current_user.id).first()
    if not session:
        return jsonify({'error': 'No active shopping session found'}), 404

    cart_item = CartItem.query.filter_by(session_id=session.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'error': 'Product not found in cart'}), 404

    cart_item.quantity = quantity
    cart_item.modified_at = datetime.now()

    session.total_before_discount = sum(item.product.price * item.quantity for item in session.cart_items)
    session.total_items = sum(item.quantity for item in session.cart_items)
    session.total_discount = sum((item.product.discount.percent / 100) * item.product.price * item.quantity for item in session.cart_items if item.product.discount)
    session.total = session.total_before_discount - session.total_discount
    session.modified_at = datetime.now()

    db.session.commit()

    return redirect(url_for('add_to_cart.show_cart'))