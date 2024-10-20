from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from extensions import db
from models import CartItem, ShoppingSession
from models.favourite import Favourite
from models.product import Product, ProductCategory, ProductInventory, ProductImage, Brand
from datetime import datetime

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/shop', methods=['GET'])
@login_required
def home():
    key_search = request.args.get('keySearch')
    if key_search:
        products = Product.query.filter(Product.name.contains(key_search)).all()
    else:
        products = Product.query.all()

    brands = Brand.query.all()
    categories = ProductCategory.query.all()
    return render_template('shop.html', user=current_user, products=products, brands=brands, categories=categories)


@shop_bp.route('/filter-products', methods=['GET'])
@login_required
def filter_products():
    category_id = request.args.get('category_filter')
    brand_id = request.args.get('brand_filter')
    price_min = request.args.get('price_min')
    price_max = request.args.get('price_max')

    query = Product.query

    if category_id:
        query = query.filter_by(category_id=category_id)
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    if price_min:
        query = query.filter(Product.price >= price_min)
    if price_max:
        query = query.filter(Product.price <= price_max)

    products = query.all()
    categories = ProductCategory.query.all()
    brands = Brand.query.all()

    return render_template('shop.html', products=products, categories=categories, brands=brands, user=current_user)


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
        discount_id = request.form.get('discount_id')
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
            SKU=product_sku,
            category_id=category_id,
            brand_id=brand_id,
            inventory_id=new_inventory.id,
            price=product_price,
            discount_id=discount_id,
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
