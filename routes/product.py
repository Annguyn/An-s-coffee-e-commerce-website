from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import csrf, db
from models import ShoppingSession
from models.order import ShippingMethod, OrderDetails, OrderItems
from models.payment import BillingInformation, PaymentDetails
from models.product import Product, ProductCategory, ProductInventory, ProductImage, Comment
from flask_login import current_user, login_required
from routes.cart import show_cart

product_bp = Blueprint('product', __name__)


@product_bp.route('/product/<int:product_id>')
def show_product(product_id):
    product = Product.query.get(product_id)
    images = ProductImage.query.filter_by(product_id=product_id).all()
    products = Product.query.all()
    categories = ProductCategory.query.all()
    comments = Comment.query.filter_by(product_id=product_id).all()
    if comments:
        average_rating = sum(comment.rating for comment in comments) / len(comments)
    else:
        average_rating = 0

    total_ratings = len(comments)
    return render_template('product-details.html',average_rating=average_rating, user=current_user,categories=categories,
                           product=product, images=images , products=products, comments=comments)
@product_bp.route('/product/<int:product_id>/add_comment', methods=['POST'])
def add_comment(product_id):
    user_name = request.form.get('user_name')
    rating = request.form.get('rating')
    text = request.form['text']

    comment = Comment(user_name=user_name, rating=rating, text=text, product_id=product_id)
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('product.show_product', product_id=product_id))