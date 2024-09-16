from flask import Blueprint, render_template

# Define the Blueprint
account_bp = Blueprint('account', __name__)


@account_bp.route('/account')
def account():
    return render_template('account.html')
