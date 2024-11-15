import random
import string
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from extensions import csrf, db
from flask_mail import Mail, Message
from models import User  # Assuming you have a User model

verify_bp = Blueprint('verify', __name__)
mail = Mail()

@verify_bp.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(username=email).first()
        if user:
            code = ''.join(random.choices(string.digits, k=6))
            session['verification_code'] = code
            session['reset_email'] = email

            msg = Message('Your Verification Code', sender='jobhuntly@gmail.com', recipients=[email])
            msg.body = f'Your verification code is {code}'
            mail.send(msg)

            flash('Verification code sent to your email.')
            return redirect(url_for('verify.show_verify'))
        else:
            flash('Email not found.')
    return render_template('forget-password.html', user=current_user)

@verify_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        email = session.get('reset_email')
        if email:
            user = User.query.filter_by(username=email).first()
            if user:
                user.set_password(new_password)
                db.session.commit()
                flash('Password reset successfully.')
                return redirect(url_for('index.home'))
            else:
                flash('User not found.')
        else:
            flash('Session expired. Please try again.')
            return redirect(url_for('verify.forget_password'))
    return render_template('reset-password.html')

@verify_bp.route('/verify')
def show_verify():
    if 'reset_email' in session:
        return render_template('verify.html')
    else:
        flash('Session expired. Please try again.')
        return redirect(url_for('verify.forget_password'))

@verify_bp.route('/verify_code', methods=['POST'])
def verify_code():
    input_code = request.form['verification_code']
    stored_code = session.get('verification_code')

    if input_code == stored_code:
        flash('Verification successful.')
        return redirect(url_for('verify.reset_password'))
    else:
        flash('Invalid verification code.')
        return redirect(url_for('verify.show_verify'))