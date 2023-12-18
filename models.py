from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func
from datetime import datetime

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask import current_app
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# ...

class accounts(db.Model):

    with open('static/images/defulat_image.jpg', 'rb') as image_file:
        default_image = image_file.read()
    

    id = db.Column(db.Integer, primary_key=True)
    profile = db.Column(db.LargeBinary, nullable=False, default=default_image)
    mime_type = db.Column(db.String(50), nullable=False)
    sales = db.Column(db.Float, nullable=False,default = 0)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    account_type = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False, default='address')
    password = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    is_suspended = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
            return accounts.query.get(user_id)
        except:
            return None
    def __repr__(self):
        return f'<Student {self.username}>'

#cart
class cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    shop_name = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_image = db.Column(db.LargeBinary, nullable=False)
    mime_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default = 1)
    

    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())


    def __repr__(self):
        return f'<cart {self.product_name}>'
    
#audit trail
class auditTrail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=func.now())
    user = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)

#seller's product
#cart
class Product(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        seller_id = db.Column(db.Integer, nullable=False)
        product_name = db.Column(db.String(100), nullable=False)
        product_details = db.Column(db.String(100), nullable=False)
        product_image = db.Column(db.LargeBinary, nullable=False)
        mime_type = db.Column(db.String(50), nullable=False)
        category = db.Column(db.String(100), nullable=False)
        price = db.Column(db.Float, nullable=False)
        quantity = db.Column(db.Integer, nullable=False)
        sold = db.Column(db.Integer, nullable=False, default = 0)
        order_quantity = db.Column(db.Integer, nullable=False, default = 1)
        created_at = db.Column(db.DateTime(timezone=True),
                            server_default=func.now())
        ratings = relationship('Rating', backref='product', lazy=True)
        
        #count the number of users who rated the product
        def num_ratings(self):
            return Rating.query.filter_by(product_id=self.id).count()

        def __repr__(self):
            return f'<product {self.product_name}>'
        
class DisabledProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_details = db.Column(db.String(100), nullable=False)
    product_image = db.Column(db.LargeBinary, nullable=False)
    mime_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)  # You may want to link this to a user in your system
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


    

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    seller_name = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_details = db.Column(db.String(100), nullable=False)
    product_image = db.Column(db.LargeBinary, nullable=False)
    mime_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(100), nullable=False, default='placed')
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __repr__(self):
        return f'<allOrders {self.product_name}>'

class customerOrders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    product_image = db.Column(db.LargeBinary, nullable=False)
    mime_type = db.Column(db.String(50), nullable=False)
    customer_name= db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(100), nullable=False, default='placed')
    product_details = db.Column(db.String(100), nullable=False)
    orderdate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())



    def __repr__(self):
        return f'<customerOrders {self.product_name}>'

