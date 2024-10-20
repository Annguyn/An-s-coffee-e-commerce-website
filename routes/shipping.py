from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from extensions import db
from models import OrderDetails, ShoppingSession
from models.payment import BillingInformation
from models.product import Product, ProductCategory, ProductInventory
from datetime import datetime

shipping_bp = Blueprint('shipping', __name__)

@shipping_bp.route('/shipping')
@login_required
def show_shipping():
    billing_information = BillingInformation.query.filter_by(user_id=current_user.id).order_by(BillingInformation.modified_at.desc()).first()
    shopping_session = ShoppingSession.query.filter_by(user_id=current_user.id).order_by(ShoppingSession.modified_at.desc()).first()
    cart_items = shopping_session.cart_items
    products = {}
    for item in cart_items:
        product = Product.query.get(item.product_id)
        products[item.product_id] = product
    return render_template('shipping.html', user=current_user, billing_information=billing_information,
                           session=shopping_session)

@shipping_bp.route('/shipping', methods=['POST'])
@login_required
def update_shipping():
    # billing_information = BillingInformation.query.filter_by(user_id=current_user.id).first()
    # if billing_information:
        # billing_information.shipping_method_id = request.form['shipping']
        # db.session.commit()
    return redirect(url_for('payment.show_payment'))