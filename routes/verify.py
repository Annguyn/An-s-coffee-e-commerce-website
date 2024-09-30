import random
import string
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from extensions import csrf, db
from flask_mail import Mail, Message

verify_bp = Blueprint('verify', __name__)
mail = Mail()

@verify_bp.route('/verify')
def show_verify():
    if current_user.is_authenticated:
        email = current_user.username
        code = ''.join(random.choices(string.digits, k=6))
        session['verification_code'] = code

        msg = Message('Your Verification Code', sender='jobhuntly@gmail.com', recipients=[email])
        msg.body = f'Your verification code is {code}'
        mail.send(msg)

        flash('Verification code sent to your email.')
    return render_template('verify.html')

@verify_bp.route('/verify_code', methods=['POST'])
def verify_code():
    input_code = request.form['verification_code']
    stored_code = session.get('verification_code')

    if input_code == stored_code:
        flash('Email verified successfully.')
        user = current_user
        user.email_verified = True
        db.session.commit()
        return redirect(url_for('index.home'))
    else:
        flash('Invalid verification code.')
        return redirect(url_for('verify.show_verify'))