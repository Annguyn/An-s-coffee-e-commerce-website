from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from extensions import db
from models import CartItem, ShoppingSession
from models.favourite import Favourite
from models.product import Product, ProductCategory, ProductInventory, ProductImage, Brand
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter

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
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_sku = request.form['product_sku']
        category_id = request.form['category_id']
        brand_id = request.form['brand_id']
        product_price = request.form['product_price']
        quantity = request.form['quantity']
        product_image = request.files['product_image'].read()
        additional_images = request.files.getlist('additional_images')
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
            image=product_image,
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

        flash('Product uploaded successfully!', 'success')
        return redirect(url_for('shop.home'))

    categories = ProductCategory.query.all()
    brands = Brand.query.all()
    return render_template('upload_product.html', user=current_user, categories=categories, brands=brands)
