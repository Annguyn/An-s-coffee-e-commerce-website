from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import csrf
from models import ShoppingSession, CartItem
from models.favourite import Favourite
from models.product import Product, ProductCategory, ProductInventory
from flask_login import current_user, login_required
from routes.cart import show_cart

index_bp = Blueprint('index', __name__)

from flask import session


@index_bp.before_request
def load_user_data():
    if current_user.is_authenticated:
        session['num_favorite_products'] = Favourite.query.filter_by(user_id=current_user.id).count()
        shopping_session = ShoppingSession.query.filter_by(user_id=current_user.id).first()
        session['num_cart_items'] = CartItem.query.filter_by(session_id=shopping_session.id).count() if shopping_session else 0
@index_bp.route('/')
def home():
    products = Product.query.all()
    categories = ProductCategory.query.all()
    return render_template('index.html', user=current_user, products=products, categories=categories)