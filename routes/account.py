from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_security import Security, SQLAlchemyUserDatastore, login_user
from models.user import User
from extensions import db
from utils import get_logged_in_user

# Define the Blueprint
account_bp = Blueprint('account', __name__)

# Initialize Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, None)
security = Security()

@account_bp.route('/account')
def account():
    user = get_logged_in_user()
    return render_template('account.html', user=user)

@account_bp.route('/account/sign-in', methods=['POST'])
def sign_in():
    username = request.form['username']
    password = request.form['password']
    user = user_datastore.find_user(username=username)

    if user and user.verify_password(password):
        login_user(user)
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin  # Store admin status in session
        flash('Sign in successful!', 'success')
        return redirect(url_for('hello_world', user=user))
    else:
        flash('Invalid username or password', 'danger')
    return redirect(url_for('account.account'))

# routes/account.py
# routes/account.py
@account_bp.route('/account/sign-up', methods=['POST'])
def sign_up():
    full_name = request.form['full_name']
    email = request.form['email']
    password = request.form['password']
    repeat_password = request.form['repeat_password']
    is_admin = request.form.get('is_admin', False)  # Optional admin flag

    if password != repeat_password:
        flash('Passwords do not match', 'danger')
        return redirect(url_for('account.account'))

    if user_datastore.find_user(username=email):
        flash('Email already exists', 'danger')
    else:
        first_name, last_name = (full_name.split(' ', 1) + [''])[:2]
        time = datetime.now()
        new_user = user_datastore.create_user(
            username=email,
            first_name=first_name,
            last_name=last_name,
            created_at=time,
            modified_at=time,
            is_admin=is_admin,
            active=True,  # Set active to True
            roles=[]  # Initialize with an empty list of roles
        )
        new_user.set_password(password)
        db.session.commit()
        flash('Sign up successful!', 'success')
        return redirect(url_for('account.account'))
    return redirect(url_for('account.account'))