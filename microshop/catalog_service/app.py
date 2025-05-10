import os
from dotenv import load_dotenv

load_dotenv()
from flask import Flask, render_template,request
from config import Config
from catalog_service.models import Product, db
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_migrate import Migrate

time_live_token = 6000 # в секундах

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate()
migrate.init_app(app, db)

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

@app.route('/')
def catalog():
    current_user_id = verify_token(request.cookies.get('auth_token'))[0]
    return render_template('index.html', products=Product.query.all(), current_user_id=current_user_id)

@app.route('/product')
def product():
    product_id = request.args['product_id']
    if product_id.isdigit():
        product_id = int(product_id)
        current_user_id = verify_token(request.cookies.get('auth_token'))[0]
        return render_template('product.html', product=Product.query.get(product_id), current_user_id=current_user_id)
    return 'Товар не найден!'

@app.route('/found_products/<int:user_id>', methods=['POST'])
def found_products(user_id):
    if request.method == 'POST':
        found_product = request.form.get('found_product')
        found_product = str(found_product)
        products = Product.query.all()
        new_catalog = []
        for item in products:
            if found_product.lower() in item.name.lower():
                new_catalog.append(item)
        return render_template('index.html', products=new_catalog, current_user_id=user_id)
    return render_template('404.html', error='Ошибка поиска товара')

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=5001)
