from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import csrf
from models import ShoppingSession, CartItem
from models.favourite import Favourite
from models.product import Product, ProductCategory, ProductInventory
from flask_login import current_user, login_required


deliver_bp = Blueprint('deliver', __name__)


@deliver_bp.route('/deliver')
def deliver():
    return render_template('deliver-info.html')