import hashlib
import hmac
import traceback
import urllib
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
    shipping_method = ShippingMethod.query.get(billing_information.shipping_method_id)
    return render_template('payment.html', user=current_user, billing_information=billing_information,
                           cart_items=cart_items, products=products, session=shopping_session,
                           shipping_method=shipping_method)

from services.zalopay import create_zalopay_order, config, query_zalopay_order

import logging

logging.basicConfig(level=logging.DEBUG)

@payment_bp.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    data = request.form
    payment_method = data.get('payment-methods')
    payment_method = 'zalopay-method'
    logging.debug(f"Received payment method: {payment_method}")

    if payment_method == 'zalopay-method':
        billing_information = BillingInformation.query.filter_by(user_id=current_user.id).first()
        shopping_session = ShoppingSession.query.filter_by(user_id=current_user.id).first()
        cart_items = shopping_session.cart_items
        order_detail = OrderDetails(
            user_id=current_user.id,
            total=shopping_session.total + ShippingMethod.query.get(billing_information.shipping_method_id).price,
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
        order_id = generate_order_id()
        description = "Payment for order {}".format(order_id)
        result = create_zalopay_order(amount, description)

        if result['return_code'] == 1:
            payment_detail.transaction_id = result['app_trans_id']
            db.session.commit()
            logging.info(f"Payment for transaction {order_id} was successful.")
            return redirect(result['order_url'])
        else:
            return jsonify({'error': 'Payment failed'}), 400
    else:
        return jsonify({'error': 'Invalid payment method'}), 400



@payment_bp.route('/callback', methods=['POST'])
def callback():
    result = {}
    try:
        cbdata = request.json
        mac = hmac.new(config['key2'].encode(), cbdata['data'].encode(), hashlib.sha256).hexdigest()
        logging.info('Processing callback data')

        # kiểm tra callback hợp lệ (đến từ ZaloPay server)
        if mac != cbdata['mac']:
            # callback không hợp lệ
            result['return_code'] = -1
            result['return_message'] = 'mac not equal'
            logging.error('MAC not equal')
        else:
            # thanh toán thành công

            dataJson = json.loads(cbdata['data'])
            app_trans_id = dataJson['app_trans_id']
            logging.info('Payment successful for transaction')
            logging.info("update order's status = success where app_trans_id = " + app_trans_id)
            payment_detail= PaymentDetails.query.filter_by(transaction_id=app_trans_id).first()
            payment_detail.status = 'success'
            db.session.commit()
            result['return_code'] = 1
            result['return_message'] = 'success'
    except Exception as e:
        logging.error('Error processing callback data')
        logging.error(traceback.format_exc())
        result['return_code'] = 0 # ZaloPay server sẽ callback lại (tối đa 3 lần)
        result[' e'] = str(e)

    # thông báo kết quả cho ZaloPay server
    return jsonify(result)

@payment_bp.route('/payment_status/', methods=['POST'])
def payment_status():
    try:
        data = request.json
        app_trans_id = data.get('app_trans_id')

        if not app_trans_id:
            return jsonify({'error': 'app_trans_id is required'}), 400

        params = {
            "app_id": config["app_id"],
            "app_trans_id": app_trans_id
        }

        data = "{}|{}|{}".format(config["app_id"], params["app_trans_id"], config["key1"])  # app_id|app_trans_id|key1
        params["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

        response = urllib.request.urlopen(url='https://sb-openapi.zalopay.vn/v2/query', data=urllib.parse.urlencode(params).encode())
        result = json.loads(response.read())

        return jsonify(result)
    except Exception as e:
        logging.error('Error querying payment status')
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

def generate_order_id():
    return datetime.now().strftime('%Y%m%d%H%M%S')

def calculate_order_amount(data):
    order_detail = OrderDetails.query.filter_by(user_id=current_user.id).order_by(OrderDetails.id.desc()).first()
    if order_detail:
        return int(order_detail.total)
    return 0
