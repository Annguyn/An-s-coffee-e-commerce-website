from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import csrf
from models import ShoppingSession, CartItem, OrderDetails, OrderItems
from models.favourite import Favourite
from models.product import Product, ProductCategory, ProductInventory
from flask_login import current_user, login_required


styleguide_bp = Blueprint('styleguide', __name__)

@styleguide_bp.route('/styleguide')
def show_styleguide():
    return render_template('styleguide.html')