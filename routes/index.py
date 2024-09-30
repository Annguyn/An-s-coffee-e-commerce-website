from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import csrf
from models import ShoppingSession, CartItem
from models.favourite import Favourite
from models.product import Product, ProductCategory, ProductInventory
from flask_login import current_user, login_required
from routes.cart import show_cart

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def home():
    products = Product.query.all()
    categories = ProductCategory.query.all()

    if current_user.is_authenticated:
        num_favorite_products = Favourite.query.filter_by(user_id=current_user.id).count()
        session = ShoppingSession.query.filter_by(user_id=current_user.id).first()
        num_cart_items = CartItem.query.filter_by(session_id=session.id).count() if session else 0
        return render_template('index.html', user=current_user, products=products,
                               categories=categories, num_favorite_products=num_favorite_products,
                               num_cart_items=num_cart_items)
    else:
        return render_template('index.html', products=products, categories=categories)