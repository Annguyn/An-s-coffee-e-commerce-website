from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User
from extensions import db

# Define the Blueprint
account_bp = Blueprint('account', __name__)

@account_bp.route('/account')
def account():
    return render_template('account.html')

@account_bp.route('/account/sign-in', methods=['POST'])
def sign_in():
    username = request.form['username']
    password = request.form['password']
    user = db.session.query(User).filter_by(username=username, password=password).first()
    if user:
        flash('Sign in successful!', 'success')
        return redirect(url_for('hello_world'))
    else:
        flash('Invalid username or password', 'danger')
    return redirect(url_for('account.account'))

@account_bp.route('/account/sign-up', methods=['POST'])
def sign_up():
    full_name = request.form['full_name']
    print(full_name)
    email = request.form['email']
    print(email)
    password = request.form['password']
    print(password)
    repeat_password = request.form['repeat_password']
    print(repeat_password)

    if password != repeat_password:
        flash('Passwords do not match', 'danger')
        print('Passwords do not match')
        return redirect(url_for('account.account'))

    if db.session.query(User).filter_by(username=email).first():
        flash('Email already exists', 'danger')
        print('Email already exists')
        for user in db.session.query(User).all():
            print(user.username)
            print(user.password)
            print(user.first_name)
    else:
        first_name, last_name = (full_name.split(' ', 1) + [''])[:2]
        time = datetime.now()
        new_user = User(username=email, password=password, first_name=first_name, last_name=last_name, created_at=time, modified_at=time)
        db.session.add(new_user)
        print('Sign up successful')
        db.session.commit()
        flash('Sign up successful!', 'success')
        return redirect(url_for('account.account'))
    return redirect(url_for('account.account'))