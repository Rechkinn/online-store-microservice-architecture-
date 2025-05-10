from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# db = SQLAlchemy(app)

db = SQLAlchemy()
migrate = Migrate()

class User(db.Model, UserMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "phone": self.phone,
        }

class Cart(db.Model):
    __tablename__ = "carts"

    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "cart_id": self.cart_id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "count": self.count,
        }
