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


@admin_bp.route('/admin/orders', methods=['GET', 'POST'])
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index.home'))

    if request.method == 'POST':
        order_id = request.form.get('order_id')
        action = request.form.get('action')
        order = OrderDetails.query.get(order_id)
        if order:
            if action == 'confirm':
                order.status = 'Confirmed'
            elif action == 'reject':
                order.status = 'Rejected'
            db.session.commit()
            flash(f'Order {order_id} has been {order.status.lower()}.', 'success')
        else:
            flash('Order not found.', 'danger')

    orders = OrderDetails.query.filter_by(status='Pending').all()
    return render_template('admin_order.html', orders=orders)