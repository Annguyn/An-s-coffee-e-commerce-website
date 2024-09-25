from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from models import db, favourite, Product
from models.favourite import Favourite
from extensions import db

add_to_favourite_bp = Blueprint('add_to_favourite', __name__)


@add_to_favourite_bp.route('/add_to_favourites', methods=['POST'])
@login_required
def add_to_favourites():
    product_id = request.form.get('product_id')
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    favourite = Favourite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if favourite:
        return jsonify({'message': 'Product already in favourites'}), 200

    new_favourite = Favourite(user_id=current_user.id, product_id=product_id)
    db.session.add(new_favourite)
    db.session.commit()

    return jsonify({'message': 'Product added to favourites'}), 200