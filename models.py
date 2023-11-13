from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
db = SQLAlchemy()

# ...

class accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    account_type = db.Column(db.String(80), nullable=False)
    password = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    is_suspended = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f'<Student {self.username}>'
    
#cart
class cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    shop_name = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_image = db.Column(db.LargeBinary, nullable=False)
    mime_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)


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
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __repr__(self):
        return f'<product {self.product_name}>'
