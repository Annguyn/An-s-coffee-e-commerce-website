from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_security import Security, SQLAlchemyUserDatastore, login_user
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash

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

    status = request.args.get('status')
    query = OrderDetails.query
    if status:
        query = query.filter_by(status=status)
    orders = query.all()

    return render_template('admin_order.html', orders=orders)

