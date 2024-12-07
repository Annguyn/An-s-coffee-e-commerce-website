import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import csrf, db
from models import ShoppingSession
from models.order import ShippingMethod, OrderDetails, OrderItems
from models.payment import BillingInformation, PaymentDetails
from models.product import Product, ProductCategory, ProductInventory, ProductImage, Comment
from flask_login import current_user, login_required
from routes.cart import show_cart

product_bp = Blueprint('product', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@product_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def show_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        if current_user.is_authenticated and current_user.is_admin:
            product.name = request.form['name']
            product.price = request.form['price']
            product.desc = request.form['desc']
            product.quantity = request.form['quantity']
            db.session.commit()
            flash('Product updated successfully', 'success')
        else:
            flash('You do not have permission to update this product', 'danger')
        return redirect(url_for('product.show_product', product_id=product_id))

    images = ProductImage.query.filter_by(product_id=product_id).all()
    products = Product.query.all()
    categories = ProductCategory.query.all()
    comments = Comment.query.filter_by(product_id=product_id).all()
    if comments:
        average_rating = sum(comment.rating for comment in comments) / len(comments)
    else:
        average_rating = 0

    total_ratings = len(comments)

    has_purchased = False
    if current_user.is_authenticated:
        has_purchased = OrderItems.query.join(OrderDetails).filter(
            OrderDetails.user_id == current_user.id,
            OrderItems.product_id == product_id
        ).count() > 0

    return render_template('product-details.html', average_rating=average_rating, user=current_user, categories=categories,
                           product=product, images=images, products=products, comments=comments, has_purchased=has_purchased)

@product_bp.route('/product/<int:product_id>/add_comment', methods=['POST'])
def add_comment(product_id):
    user_name = request.form.get('user_name')
    rating = request.form.get('rating')
    text = request.form['text']

    comment = Comment(user_name=user_name, rating=rating, text=text, product_id=product_id)
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('product.show_product', product_id=product_id))

@product_bp.route('/search_by_image', methods=['POST'])
def search_by_image():
    logger.debug("search_by_image route called")
    if 'product_image' not in request.files:
        logger.debug("No product_image in request.files")
        return redirect(url_for('shop.home'))

    file = request.files['product_image']
    if file.filename == '':
        logger.debug("Empty filename in request.files['product_image']")
        return redirect(url_for('shop.home'))

    if file:
        from services.image_search import predict_product
        product_name = predict_product(file)
        logger.debug(f"Predicted product name: {product_name}")
        return redirect(url_for('shop.home', keySearch=product_name))