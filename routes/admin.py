from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_security import Security, SQLAlchemyUserDatastore, login_user
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash
from flask_paginate import Pagination, get_page_parameter

from models import OrderDetails, ProductCategory
from models.coupon import Coupon
from models.user import User
from extensions import db
from utils import get_logged_in_user

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/orders', methods=['GET'])
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index.home'))

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 9
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    status = request.args.get('status')
    query = OrderDetails.query

    if status:
        query = query.filter_by(status=status)

    if sort_order == 'desc':
        query = query.order_by(getattr(OrderDetails, sort_by).desc())
    else:
        query = query.order_by(getattr(OrderDetails, sort_by).asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items

    return render_template('admin_order.html',user=current_user, orders=orders, pagination=pagination, sort_by=sort_by, sort_order=sort_order, status=status)

@admin_bp.route('/add_product_category', methods=['GET', 'POST'])
@login_required
def add_product_category():
    if not current_user.is_admin:
        return redirect(url_for('index.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('desc')
        image = request.files.get('image').read() if request.files.get('image') else None

        if name:
            new_category = ProductCategory(
                name=name,
                desc=desc,
                image=image,
                created_at=datetime.now(),
                modified_at=datetime.now()
            )
            db.session.add(new_category)
            db.session.commit()
            flash('Product category added successfully!', 'success')
            return redirect(url_for('admin.add_product_category'))
        else:
            flash('Please provide a category name.', 'danger')

    return render_template('add_category.html')

@admin_bp.route('/add_coupon', methods=['GET', 'POST'])
@login_required
def add_coupon():
    if not current_user.is_admin:
        return redirect(url_for('index.home'))

    categories = ProductCategory.query.all()

    if request.method == 'POST':
        code = request.form.get('code')
        min_payment = request.form.get('min_payment')
        category_id = request.form.get('category_id')
        percent = request.form.get('percent')
        max_discount = request.form.get('max')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        if code and min_payment and category_id and percent and max_discount and start_time and end_time:
            new_coupon = Coupon(
                code=code,
                min_payment=float(min_payment),
                category_id=int(category_id),
                percent=float(percent),
                max=float(max_discount),
                start_time=datetime.fromisoformat(start_time),
                end_time=datetime.fromisoformat(end_time)
            )
            db.session.add(new_coupon)
            db.session.commit()
            flash('Coupon added successfully!', 'success')
            return redirect(url_for('admin.add_coupon'))
        else:
            flash('Please provide all required fields.', 'danger')

    return render_template('add_coupon.html', categories=categories)