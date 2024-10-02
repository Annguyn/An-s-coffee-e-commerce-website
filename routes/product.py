from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import csrf, db
from models import ShoppingSession
from models.order import ShippingMethod, OrderDetails, OrderItems
from models.payment import BillingInformation, PaymentDetails
from models.product import Product, ProductCategory, ProductInventory, ProductImage
from flask_login import current_user, login_required
from routes.cart import show_cart

product_bp = Blueprint('product', __name__)


@product_bp.route('/product/<int:product_id>')
def show_product(product_id):
    product = Product.query.get(product_id)
    images = ProductImage.query.filter_by(product_id=product_id).all()
    products = Product.query.all()
    categories = ProductCategory.query.all()
    return render_template('product-details.html', categories=categories,
                           product=product, images=images)
