import os

from alembic.ddl.base import format_server_default
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template,request,redirect, url_for, flash, make_response
from config import Config
from models import Cart, User, db
from flask_migrate import Migrate
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from catalog_service.connect_db import *

# from catalog_service.models import Product

time_live_token = 6000 # в секундах

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate()
migrate.init_app(app, db)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        name = request.form.get('user_name')
        email = request.form.get('user_email')
        password = request.form.get('user_password')
        phone = request.form.get('user_phone')

        if name and email and password and phone:
            new_user = User(name=name, email=email,password=password,phone=phone)
            db.session.add(new_user)
            db.session.commit()
            return redirect('http://127.0.0.1:5002/login')
        return 'ошибка создания нового пользователя'
    return render_template('register.html')

@staticmethod
def check_email(email_for_test):
    email_list = email_for_test.split('@')
    if(len(email_list) == 2):
        email_for_test = email_list[1]
        email_list = email_for_test.split('.')
        if(len(email_list) == 2):
            return print('всё четко')
        return print('введено без символа .')
    return print('введено без символа @')

@staticmethod
def generate_token(user_id):
    salt = 'auth-token-salt'
    s = URLSafeTimedSerializer(os.getenv('SECRET_KEY'), salt=salt)
    return s.dumps({'user_id': user_id})

@staticmethod
def verify_token(token):
    salt = 'auth-token-salt'
    s = URLSafeTimedSerializer(os.getenv('SECRET_KEY'), salt=salt)
    try:
        data = s.loads(token, max_age=time_live_token)
    except TypeError:
        return None, 'invalid'
    except SignatureExpired:
        # токен был корректен, но «просрочен»
        return None, 'expired'
    except BadSignature:
        # токен не прошёл подпись
        return None, 'invalid'
    # всё ок, достаём user_id
    return data.get('user_id'), None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('user_email')
        password = request.form.get('user_password')

        user = User.query.filter_by(email=email).first()

        if not user or password != user.password:
            return redirect(url_for('login'))

        token = generate_token(user.user_id)

        response = make_response(redirect('http://127.0.0.1:5001'))
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=time_live_token  # 24 часа
        )
        return response
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(redirect('http://127.0.0.1:5001/'))
    response.delete_cookie('auth_token', path='/', secure=False, samesite='Lax')
    return response

@app.route('/cart')
def show_cart():
    current_user_id = verify_token(request.cookies.get('auth_token'))[0]
    carts = Cart.query.filter_by(user_id=current_user_id).all()
    products = []
    for cart in carts:
        sql = f"SELECT * FROM products WHERE id = {cart.product_id}"
        cursor.execute(sql)
        current_product_info = cursor.fetchone()
        current_product_info["count"] = cart.count
        products.append(current_product_info)
    return render_template('cart.html', current_user_id=current_user_id, list_products=products)

@app.route(f'/cart/add', methods=['POST'])
def add_cart():
    item_id = request.args['product_id']
    current_user_id = request.args['user_id']
    try:
        if not current_user_id or not current_user_id.isdigit():
            return redirect('http://127.0.0.1:5002/login')
    except AttributeError:
        return redirect('http://127.0.0.1:5002/login')
    finally:
        if item_id.isdigit():
            item_id = int(item_id)
            current_user_id = int(current_user_id)
            cart = Cart.query.filter_by(product_id = item_id, user_id = current_user_id).first()
            if not cart:
                # Добавляем товар в корзину
                new_cart = Cart(product_id = item_id, user_id = current_user_id, count = 1)
                db.session.add(new_cart)
                db.session.commit()
                # flash('Товар успешно добавлен.', 'success')
            return redirect('http://127.0.0.1:5002/cart')
        return render_template('404.html', error='Товар не найден!')

@app.route(f'/cart/up', methods=['POST'])
def up_cart():
    name_product = request.args['name_product']
    if name_product:
        new_count_product = request.form.get(f'newCount{name_product}')
        product_id = request.args['product_id']
        current_user_id = request.args['user_id']
        if new_count_product and new_count_product.isdigit():
            if product_id and product_id.isdigit():
                if current_user_id and current_user_id.isdigit():
                    new_count_product = int(new_count_product)
                    product_id = int(product_id)
                    current_user_id = int(current_user_id)
                    cart = Cart.query.filter_by(product_id=product_id, user_id=current_user_id).first()
                    cart.count = new_count_product
                    db.session.commit()
                    return redirect('http://127.0.0.1:5002/cart')
                return render_template('404.html', error='Пользователь не найден')
            return render_template('404.html', error='Товар не найден')
        return render_template('404.html', error='Неверное количество продукта')
    return render_template('404.html', error='Продукт не найден')



@app.route(f'/cart/delete', methods=['POST'])
def delete_cart():
    product_id = request.args['product_id']
    current_user_id = request.args['user_id']
    try:
        if not current_user_id or not current_user_id.isdigit():
            return redirect('http://127.0.0.1:5002/login')
    except AttributeError:
        return redirect('http://127.0.0.1:5002/login')
    finally:
        if product_id.isdigit():
            product_id = int(product_id)
            current_user_id = int(current_user_id)
            cart = Cart.query.filter_by(product_id = product_id, user_id = current_user_id).first()

            if cart:
                db.session.delete(cart)
                db.session.commit()

            return redirect('http://127.0.0.1:5002/cart')
        return render_template('404.html', error='Товар не найден!')

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=5002)
