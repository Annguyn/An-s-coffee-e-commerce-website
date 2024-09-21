from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.product import Product, ProductCategory, ProductInventory
from flask_login import current_user, login_required
index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html',user=current_user, products=products,categories = ProductCategory.query.all())

