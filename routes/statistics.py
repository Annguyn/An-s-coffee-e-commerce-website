from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from extensions import db
from models import OrderDetails, OrderItems, User, Product
from models.product import Comment, ProductCategory
from datetime import datetime

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/admin/statistics')
@login_required
def show_statistics():
    start_date = request.args.get('start_date', '2023-01-01')
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    total_orders = db.session.query(db.func.date(OrderDetails.created_at), db.func.count(OrderDetails.id)).filter(OrderDetails.created_at.between(start_date, end_date)).group_by(db.func.date(OrderDetails.created_at)).all()
    orders_by_status = db.session.query(db.func.date(OrderDetails.created_at), OrderDetails.status, db.func.count(OrderDetails.id)).filter(OrderDetails.created_at.between(start_date, end_date)).group_by(db.func.date(OrderDetails.created_at), OrderDetails.status).all()
    best_sellers = db.session.query(Product.name, db.func.sum(OrderItems.quantity)).join(OrderItems).group_by(Product.id).order_by(db.func.sum(OrderItems.quantity).desc()).limit(5).all()
    best_ratings = db.session.query(Product.name, db.func.avg(Comment.rating)).join(Comment).group_by(Product.id).order_by(db.func.avg(Comment.rating).desc()).limit(5).all()

    orders_by_status_data = {}
    for date, status, count in orders_by_status:
        date_str = date if isinstance(date, str) else date.strftime('%Y-%m-%d')
        if status not in orders_by_status_data:
            orders_by_status_data[status] = {}
        orders_by_status_data[status][date_str] = count

    all_dates = {date if isinstance(date, str) else date.strftime('%Y-%m-%d') for date, _ in total_orders}
    for status in orders_by_status_data:
        for date in all_dates:
            orders_by_status_data[status].setdefault(date, 0)

    chart_data = {
        "labels": sorted(all_dates),
        "datasets": [
            {
                "label": status,
                "data": [orders_by_status_data[status].get(date, 0) for date in sorted(all_dates)],
                "fill": False
            }
            for status in orders_by_status_data
        ]
    }

    return render_template(
        'admin_statistics.html',
        total_orders=total_orders,
        orders_by_status=orders_by_status,
        best_sellers=best_sellers,
        best_ratings=best_ratings,
        chart_data=chart_data,
        user=current_user,
        categories=ProductCategory.query.all()
    )

@statistics_bp.route('/statistics')
@login_required
def show_user_statistics():
    start_date = request.args.get('start_date', '2023-01-01')
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    total_orders = db.session.query(db.func.count(OrderDetails.id)).filter(OrderDetails.user_id == current_user.id).scalar()
    total_money_paid = db.session.query(db.func.sum(OrderDetails.total)).filter(OrderDetails.user_id == current_user.id).scalar()

    favorite_products = db.session.query(
        Product.name, db.func.count(OrderItems.product_id)
    ).select_from(OrderItems).join(
        Product, OrderItems.product_id == Product.id
    ).join(
        OrderDetails, OrderItems.order_id == OrderDetails.id
    ).filter(
        OrderDetails.user_id == current_user.id
    ).group_by(
        Product.id
    ).order_by(
        db.func.count(OrderItems.product_id).desc()
    ).limit(5).all()

    favorite_categories = db.session.query(
        ProductCategory.name, db.func.count(OrderItems.product_id)
    ).select_from(OrderItems).join(
        Product, OrderItems.product_id == Product.id
    ).join(
        ProductCategory, Product.category_id == ProductCategory.id
    ).join(
        OrderDetails, OrderItems.order_id == OrderDetails.id
    ).filter(
        OrderDetails.user_id == current_user.id
    ).group_by(
        ProductCategory.name
    ).order_by(
        db.func.count(OrderItems.product_id).desc()
    ).limit(5).all()

    orders_by_status = db.session.query(
        db.func.date(OrderDetails.created_at), OrderDetails.status, db.func.count(OrderDetails.id)
    ).filter(
        OrderDetails.user_id == current_user.id,
        OrderDetails.created_at.between(start_date, end_date)
    ).group_by(
        db.func.date(OrderDetails.created_at), OrderDetails.status
    ).all()

    orders_by_status_data = {}
    for date, status, count in orders_by_status:
        date_str = date if isinstance(date, str) else date.strftime('%Y-%m-%d')
        if status not in orders_by_status_data:
            orders_by_status_data[status] = {}
        orders_by_status_data[status][date_str] = count

    all_dates = {date if isinstance(date, str) else date.strftime('%Y-%m-%d') for date, _, _ in orders_by_status}
    for status in orders_by_status_data:
        for date in all_dates:
            orders_by_status_data[status].setdefault(date, 0)

    chart_data = {
        "labels": sorted(all_dates),
        "datasets": [
            {
                "label": status,
                "data": [orders_by_status_data[status].get(date, 0) for date in sorted(all_dates)],
                "fill": False
            }
            for status in orders_by_status_data
        ]
    }

    return render_template(
        'user_statistics.html',
        total_orders=total_orders,
        total_money_paid=total_money_paid,
        favorite_products=favorite_products,
        favorite_categories=favorite_categories,
        chart_data=chart_data,
        user=current_user,
        categories=ProductCategory.query.all()
    )