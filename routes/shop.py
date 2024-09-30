from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from extensions import db
from models import CartItem, ShoppingSession
from models.favourite import Favourite
from models.product import Product, ProductCategory, ProductInventory, ProductImage
from datetime import datetime

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/shop')
@login_required
def home():
    products = Product.query.all()

    return render_template('shop.html', user=current_user, products=products)

@shop_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_sku = request.form['product_sku']
        category_id = request.form['category_id']
        product_price = request.form['product_price']
        discount_id = request.form.get('discount_id')
        product_image = request.files['product_image'].read()
        additional_images = request.files.getlist('additional_images')
        created_at = datetime.now()
        modified_at = datetime.now()

        new_inventory = ProductInventory(
            quantity=0,
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
    return render_template('upload_product.html', user=current_user, categories=categories)