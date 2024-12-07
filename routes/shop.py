from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import current_user, login_required
from extensions import db
from models import CartItem, ShoppingSession
from models.favourite import Favourite
from models.product import Product, ProductCategory, ProductInventory, ProductImage, Brand
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter

from services.get_image import train_model
from services.train_model import check_and_train_model

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/shop', methods=['GET'])
# @login_required
def home():
    key_search = request.args.get('keySearch')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 9

    query = Product.query
    if key_search:
        query = query.filter(Product.name.contains(key_search))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    brands = Brand.query.all()
    categories = ProductCategory.query.all()
    return render_template('shop.html', user=current_user, products=products, brands=brands, categories=categories, pagination=pagination)

@shop_bp.route('/filter-products', methods=['GET'])
# @login_required
def filter_products():
    category_id = request.args.get('category_filter')
    brand_id = request.args.get('brand_filter')
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 9

    query = Product.query

    if category_id:
        query = query.filter_by(category_id=category_id)
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    if price_min is not None:
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        query = query.filter(Product.price <= price_max)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    categories = ProductCategory.query.all()
    brands = Brand.query.all()

    return render_template('shop.html', products=products, categories=categories, brands=brands, user=current_user, pagination=pagination)
@shop_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_desc = request.form.get('product_desc')
        category_id = request.form.get('category_id')
        brand_id = request.form.get('brand_id')
        product_price = request.form.get('product_price', type=float)
        quantity = request.form.get('quantity', type=int)
        product_image = request.files.get('product_image')
        additional_images = request.files.getlist('additional_images')

        try:
            created_at = datetime.now()
            modified_at = datetime.now()
            new_inventory = ProductInventory(
                quantity=quantity,
                created_at=created_at,
                modified_at=modified_at
            )
            db.session.add(new_inventory)
            db.session.commit()
            new_product = Product(
                name=product_name,
                desc=product_desc,
                category_id=category_id,
                brand_id=brand_id,
                inventory_id=new_inventory.id,
                price=product_price,
                image=product_image.read(),
                created_at=created_at,
                modified_at=modified_at
            )
            db.session.add(new_product)
            db.session.commit()

            for image in additional_images:
                new_additional_image = ProductImage(
                    product_id=new_product.id,
                    image=image.read()
                )
                db.session.add(new_additional_image)

            db.session.commit()

            train_model()

            flash('Product uploaded and model trained successfully!', 'success')
            return redirect(url_for('shop.home'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('shop.upload_product'))

    categories = ProductCategory.query.all()
    brands = Brand.query.all()
    return render_template('upload_product.html', user=current_user, categories=categories, brands=brands)

