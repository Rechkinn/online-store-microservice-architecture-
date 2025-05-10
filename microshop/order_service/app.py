import os
import json
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template,request,redirect, url_for, flash, make_response
from config import Config
from models import Order_detail, Order, db
from flask_migrate import Migrate
# from user_service.models import Cart
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from catalog_service.connect_db import *

from catalog_service.app import verify_token

time_live_token = 6000 # в секундах

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate()
migrate.init_app(app, db)

@app.route('/confirm_order', methods=['GET', 'POST'])
def confirm_order():
    current_user_id = request.form.get('user_id')
    if not current_user_id.isdigit():
        return render_template('404.html', error=f'Пользователь не найден. ID = {current_user_id}')
    current_user_id = int(current_user_id)

    create_order = request.form.get('create_order')
    if not create_order:
        return render_template('404.html', error=f'Ошибка подтверждения заказа. Создание заказа: {create_order}')

    raw_json = request.form.get('products_json')  # строка JSON
    data = json.loads(raw_json)  # список dict
    products = []
    for info in data:
        if create_order == "no":
            products.append({'id': info['id'],
                             'name': info['name'],
                             'count': info['count'],
                             'price': int(info['price'].split('.')[0]),
                             'description': info['description'],
                             })
        else:
            products.append({'id': info['id'],
                             'name': info['name'],
                             'count': info['count'],
                             'price': info['price'],
                             'description': info['description'],
                             })
    full_price = 0
    for product in products:
        full_price += product['price'] * product['count']

    if request.method == 'POST' and create_order == 'yes':

        payment_method = request.form.get('payment_method')
        place_delivery = request.form.get('place_delivery')

        if payment_method and place_delivery:
            new_order = Order(user_id=current_user_id,
                              status='Заказ собирается',
                              price=full_price,
                              payment_method=payment_method,
                              place_delivery=place_delivery
                              )

            db.session.add(new_order)
            db.session.commit()

            for product in products:
                new_order_detail = Order_detail(order_id=new_order.order_id,
                                                product_id=product['id'],
                                                count_product=product['count'],
                                                )
                db.session.add(new_order_detail)
            db.session.commit()
            return redirect(f'http://127.0.0.1:5001')
        return render_template('404.html', error='Ошибка создания заказа: неверный адрес доставки или метод оплаты')
    return render_template('confirm_order.html', list_products=products, full_price=full_price, current_user_id=current_user_id)

@app.route('/order_list/<int:user_id>', methods=['GET'])
def order_list(user_id):
    user_id = str(user_id)
    if not user_id:
        return render_template('404.html', error='Авторизуйтесь в системе')
    orders = Order.query.filter_by(user_id=user_id).all()

    for order in orders:
        order.date_created_at = str(order.date_created_at).split(' ')[0]
        order.date_delivery = str(order.date_delivery).split(' ')[0]

    return render_template('order_list.html', orders=orders, current_user_id = user_id)


@app.route('/order_detail/<int:order_id>/<int:user_id>')
def order_detail(order_id,user_id):
    order_id = int(order_id)

    details = Order_detail.query.filter_by(order_id=order_id).all()
    order = Order.query.filter_by(order_id=order_id).first()
    if details:

        products = []
        help_dict = {
            'id': 0,
            'name':'',
            'price': 0,
            'count': 0
        }
        for detail in details:
            sql = f"SELECT * FROM products WHERE id = {detail.product_id}"
            cursor.execute(sql)
            current_product_info = cursor.fetchone()

            help_dict['id'] = detail.product_id
            help_dict['name'] = current_product_info['name']
            help_dict['price'] = current_product_info['price']
            help_dict['count'] = detail.count_product
            products.append(help_dict)
            help_dict = {
                'id': 0,
                'name': '',
                'price': 0,
                'count': 0
            }
        return render_template('order_detail.html', products=products, order=order, current_user_id=user_id)
    return render_template('404.html', error='Заказ не найден!')

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=5003)
