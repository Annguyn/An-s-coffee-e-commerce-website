from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_required, current_user
from models import db, favourite, Product
from extensions import db
from datetime import datetime

from models.favourite import Favourite

favourite_bp = Blueprint('favourite', __name__)

@favourite_bp.route('/favourite', methods=['GET'])
@login_required
def show_favourite():
    favourite = Favourite.query.filter_by(user_id=current_user.id).first()
    favourite_items = Favourite.query.filter_by(favourite_id=favourite.id).all()
    products = {}
    for item in favourite_items:
        product = Product.query.get(item.product_id)
        products[item.product_id] = product
    return render_template('wishlist.html', user=current_user,products= products)
