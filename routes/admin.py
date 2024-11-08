from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_security import Security, SQLAlchemyUserDatastore, login_user
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash
from flask_paginate import Pagination, get_page_parameter

from models import OrderDetails
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