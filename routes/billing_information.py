from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_required, current_user
from models import db, favourite, Product, CartItem, ShoppingSession
from extensions import db
from flask_login import current_user
from datetime import datetime

from models.payment import BillingInformation

billing_information_bp = Blueprint('billing_information', __name__)

@billing_information_bp.route('/billing_information', methods=['GET'])
@login_required
def show_billing_information():
    session = ShoppingSession.query.filter_by(user_id=current_user.id).first()
    cart_items = CartItem.query.filter_by(session_id=session.id).all()
    products = {}
    for item in cart_items:
        product = Product.query.get(item.product_id)
        products[item.product_id] = product
    return render_template('billing-information.html', user=current_user, cart_items=cart_items, session=session, products=products)

@billing_information_bp.route('/billing_information', methods=['POST'])
@login_required
def update_billing_information():
    try:
        session = BillingInformation.query.filter_by(user_id=current_user.id).first()
        if session is None:
            session = BillingInformation()
            session.user_id = current_user.id
            session.created_at = datetime.now()
            session.modified_at = datetime.now()
            db.session.add(session)

        required_fields = ['first_name', 'last_name', 'email1', 'address','province','district', 'commune', 'telephone']
        for field in required_fields:
            if field not in request.form:
                return f"Missing form data: {field}", 400

        session.first_name = request.form['first_name']
        session.last_name = request.form['last_name']
        session.email = request.form['email1']
        session.address = request.form['address']
        session.city = request.form['province']
        session.district = request.form['district']
        session.ward = request.form['commune']
        session.telephone = request.form['telephone']
        session.modified_at = datetime.now()
        db.session.commit()
    except KeyError as e:
        return f"Missing form data: {e}", 400
    return redirect(url_for('shipping.show_shipping'))