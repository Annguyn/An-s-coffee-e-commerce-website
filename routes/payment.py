import hashlib
import hmac
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, json
from langchain import requests

from extensions import csrf, db
from models import ShoppingSession
from models.order import ShippingMethod, OrderDetails, OrderItems
from models.payment import BillingInformation, PaymentDetails
from models.product import Product, ProductCategory, ProductInventory
from flask_login import current_user, login_required
from routes.cart import show_cart

payment_bp = Blueprint('payment', __name__)


@payment_bp.route('/payment')
@login_required
def show_payment():
    billing_information = BillingInformation.query.filter_by(user_id=current_user.id).first()
    shopping_session = ShoppingSession.query.filter_by(user_id=current_user.id).first()
    cart_items = shopping_session.cart_items
    products = {}
    for item in cart_items:
        product = Product.query.get(item.product_id)
        products[item.product_id] = product
    quantity = sum([item.quantity for item in cart_items])
    total = sum([item.quantity * products[item.product_id].price for item in cart_items])
    shipping_method = ShippingMethod.query.get(billing_information.shipping_method_id)
    return render_template('payment.html', user=current_user, billing_information=billing_information,
                           cart_items=cart_items, quantity=quantity, total=total, products=products,
                           shipping_method=shipping_method)


# @payment_bp.route('/payment', methods=['POST'])
# @login_required
# def update_payment():
#     billing_information = BillingInformation.query.filter_by(user_id=current_user.id).first()
#     cart_items = ShoppingSession.query.filter_by(user_id=current_user.id).first().cart_items
#     order_detail = OrderDetails(
#         user_id=current_user.id,
#         total=sum([item.quantity * Product.query.get(item.product_id).price for item in
#                    cart_items]) + ShippingMethod.query.get(billing_information.shipping_method_id).price,
#         created_at=datetime.now(),
#         payment_id=0
#     )
#     db.session.add(order_detail)
#     db.session.commit()
#     payment_detail = PaymentDetails(
#         order_id=order_detail.id,
#         amount=order_detail.total,
#         created_at=datetime.now(),
#         modified_at=datetime.now(),
#         provider="GHTK",
#         status="pending"
#     )
#     order_items = []
#     for item in cart_items:
#         order_item = OrderItems(
#             order_id=order_detail.id,
#             product_id=item.product_id,
#             quantity=item.quantity,
#             created_at=datetime.now(),
#             modified_at=datetime.now()
#         )
#         order_items.append(order_item)
#
#     db.session.add(payment_detail)
#     db.session.add_all(order_items)
#     db.session.commit()
#
#     return redirect(url_for('payment.process_payment'))


from services.zalopay import create_zalopay_order

import logging

logging.basicConfig(level=logging.DEBUG)


@payment_bp.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    data = request.form
    payment_method = data.get('payment-methods')
    payment_method='zalopay-method'
    logging.debug(f"Received payment method: {payment_method}")

    if payment_method == 'zalopay-method':
        billing_information = BillingInformation.query.filter_by(user_id=current_user.id).first()
        cart_items = ShoppingSession.query.filter_by(user_id=current_user.id).first().cart_items
        order_detail = OrderDetails(
            user_id=current_user.id,
            total=sum([item.quantity * Product.query.get(item.product_id).price for item in
                       cart_items]) + ShippingMethod.query.get(billing_information.shipping_method_id).price,
            created_at=datetime.now(),
            payment_id=0
        )
        db.session.add(order_detail)
        db.session.commit()
        payment_detail = PaymentDetails(
            order_id=order_detail.id,
            amount=order_detail.total,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            provider="GHTK",
            status="pending"
        )
        order_items = []
        for item in cart_items:
            order_item = OrderItems(
                order_id=order_detail.id,
                product_id=item.product_id,
                quantity=item.quantity,
                created_at=datetime.now(),
                modified_at=datetime.now()
            )
            order_items.append(order_item)

        db.session.add(payment_detail)
        db.session.add_all(order_items)
        db.session.commit()

        amount = calculate_order_amount(data)
        description = "Payment for order {}".format(generate_order_id())
        result = create_zalopay_order(amount, description)

        if result['return_code'] == 1:
            payment_detail.status = 'Success'
            db.session.commit()
            return redirect(result['order_url'])
        else:
            return jsonify({'error': 'Payment failed'}), 400
    else:
        return jsonify({'error': 'Invalid payment method'}), 400


def generate_order_id():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def calculate_order_amount(data):
    order_detail = OrderDetails.query.filter_by(user_id=current_user.id).first()
    if order_detail:
        return int(order_detail.total)
    return 0