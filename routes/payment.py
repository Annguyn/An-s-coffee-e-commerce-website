import hashlib
import hmac
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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

@payment_bp.route('/payment', methods=['POST'])
@login_required
def update_payment():
    billing_information = BillingInformation.query.filter_by(user_id=current_user.id).first()
    cart_items = ShoppingSession.query.filter_by(user_id=current_user.id).first().cart_items
    order_detail = OrderDetails(
        user_id=current_user.id,
        total=sum([item.quantity * Product.query.get(item.product_id).price for item in cart_items]) + ShippingMethod.query.get(billing_information.shipping_method_id).price,
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

    return redirect(url_for('payment.show_payment'))


@payment_bp.route('/payment/select')
@login_required
def select_payment():
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
    return render_template('payment-select.html', user=current_user, billing_information=billing_information,
                           cart_items=cart_items, quantity=quantity, total=total, products=products,
                           shipping_method=shipping_method)



@payment_bp.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.form
    payment_method = data.get('payment-methods')

    if payment_method == 'zalopay-method':
        return process_zalopay_payment(data)
    else:
        # Handle other payment methods
        pass

def process_zalopay_payment(data):
    order_id = generate_order_id()
    amount = calculate_order_amount(data)
    app_id = 'YOUR_ZALOPAY_APP_ID'
    key1 = 'YOUR_ZALOPAY_KEY1'
    endpoint = 'https://sandbox.zalopay.vn/v001/tpe/createorder'

    params = {
        'app_id': app_id,
        'app_trans_id': order_id,
        'app_user': 'user123',
        'amount': amount,
        'app_time': int(datetime.now().timestamp() * 1000),
        'embed_data': '{}',
        'item': '[]',
        'description': 'Payment for order {}'.format(order_id),
        'bank_code': 'zalopayapp'
    }

    data_string = '|'.join([str(params[key]) for key in sorted(params.keys())])
    params['mac'] = hmac.new(key1.encode(), data_string.encode(), hashlib.sha256).hexdigest()

    response = requests.post(endpoint, json=params)
    result = response.json()

    if result['return_code'] == 1:
        return redirect(result['order_url'])
    else:
        return jsonify({'error': 'Payment failed'}), 400

def generate_order_id():
    return datetime.now().strftime('%Y%m%d%H%M%S')

def calculate_order_amount(data):
    # Implement your logic to calculate the order amount
    return 100000  # Example amount