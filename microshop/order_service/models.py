from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from datetime import datetime, timedelta

# db = SQLAlchemy(app)

db = SQLAlchemy()
migrate = Migrate()

class Order(db.Model, UserMixin):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    date_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    date_delivery = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    payment_method = db.Column(db.String(50), nullable=False)
    place_delivery = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "price": self.price,
            "status": self.status,
            "date_created_at": self.date_created_at,
            "date_delivery": self.date_delivery,
            "payment_method": self.payment_method,
            "place_delivery": self.place_delivery,
        }

class Order_detail(db.Model):
    __tablename__ = "order_detail"

    order_detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    count_product = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "order_detail_id": self.order_detail_id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "count_product": self.count_product,
        }
