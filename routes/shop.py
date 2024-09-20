from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/shop')
@login_required
def home():
    return render_template('shop.html', user=current_user)