import os
from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    session,
    request,
    jsonify, flash
)

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_mail import Mail, Message
from wtforms.validators import Email as EmailValidator
import secrets
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from models import db, accounts, cart, auditTrail, Product, Orders, customerOrders, Rating
from sqlalchemy.sql import func
from base64 import b64encode
import base64

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "db.sqlite3"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] ='jinrishira@gmail.com'
app.config['MAIL_PASSWORD'] = 'ywgt zmbr mfvc cfbe'


db.init_app(app)
mail = Mail(app)

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), EmailValidator()], render_kw={"placeholder": "Enter your email"})
    submit = SubmitField('Send Reset Instructions', render_kw={"class": "btn btn-primary mb-3"})



# Custom Jinja2 filter to truncate text
def truncate_text(text, max_length):
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

app.jinja_env.filters['truncate_text'] = truncate_text
# FUNCTIONS FOR LOGIN
@app.route("/login", methods=["GET", "POST"])
def Login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Query the database for a user with the given username
        user = accounts.query.filter_by(email=username).first()

        if user and check_password_hash(user.password, password):
            # Password verification using check_password_hash
            session["user_id"] = user.id
            session["user_email"] = user.email
            audit_record = auditTrail(user=username, event_type='Login', description='User logged in')
            db.session.add(audit_record)
            db.session.commit()
            return redirect(url_for("LandingPage"))

        else:
            error = "Invalid email or password. Please try again."

    return render_template("login.html", error=error)

#Product rating
def calculate_average_rating(product):
    if product.ratings:
        total_rating = sum(rating.rating for rating in product.ratings)
        average_rating = total_rating / len(product.ratings)
        return average_rating
    return 0  # Return 0 if there are no ratings

@app.route("/landingpage", methods=["GET"])
def LandingPage():
    
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
    else:
        # User is not logged in, or no cart data found
        cart_count = 0
    outdoor_clothing_products = Product.query.filter_by(category="Outdoor Clothing").all()
    exercise_fitness_gear_products = Product.query.filter_by(category="Exercise & Fitness Gear").all()
    camping_hiking_gear_products = Product.query.filter_by(category="Camping & Hiking Gear").all()
    sports_equipment_products = Product.query.filter_by(category="Sports Equipment").all()
    
      # Query products and their ratings using lazy loading
    products = Product.query.all()
    for product in products:
        
        product.average_rating = calculate_average_rating(product)

    for product in outdoor_clothing_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")
        
    for product in exercise_fitness_gear_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")
        
    for product in camping_hiking_gear_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")

    for product in sports_equipment_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")

    return render_template("customers/landingpage.html", cart_count=cart_count, outdoor_clothing=outdoor_clothing_products,
    exercise_products=exercise_fitness_gear_products,camping_products=camping_hiking_gear_products, sports_products=sports_equipment_products
    ,calculate_average_rating=calculate_average_rating)


# END OF FUNCTIONS LOGIN
@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if request.method == 'POST':
        # Check if the product with the given ID exists in your database
        product = Product.query.get(product_id)

        product_name = product.product_name
        if product:
            # Assuming you have a customer ID, seller ID, and shop name, update these accordingly
            customer_id = session['user_id']
            seller_id = product.seller_id
            shop_name = "Your Shop Name"

            new_product = cart(
                customer_id=customer_id,
                seller_id=seller_id,
                shop_name=shop_name,
                product_name=product.product_name,
                product_image=product.product_image,
                mime_type=product.mime_type,
                category=product.category,  # Update with the actual category
                description=product.product_details,
                price=product.price
            )

            db.session.add(new_product)
            email = session["user_email"]
            audit_record = auditTrail(user=email, event_type='Add to cart', description=f'{product_name} added to cart')
            db.session.add(audit_record)
            db.session.commit()
            return jsonify({"message": "Product added to cart successfully"})
        else:
            
            return jsonify({'error': 'Product not found'})

    return jsonify({'error': 'Invalid request'})

@app.route("/get-cart-count", methods=["GET"])
def get_cart_count():
    # Get the user's ID from the session
    user_id = session.get("user_id")

    if user_id is not None:
        # Calculate the cart count specific to the logged-in user
        cart_count = db.session.query(cart).filter_by(customer_id=user_id).count()
    else:
        # If the user is not logged in, return a count of 0
        cart_count = 0

    # Return the cart count as JSON
    return jsonify({"count": cart_count})


@app.route("/remove-from-cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    try:
        # Find the product in the cart by its ID
        product_to_remove = cart.query.get(product_id)
        product_name = product_to_remove.product_name
        if product_to_remove:
            # Remove the product from the cart
            db.session.delete(product_to_remove)
            db.session.commit()

            updated_total_price = get_cart_total()
            
             # Add record for audit trail
            email = session["user_email"]
            audit_record = auditTrail(user=email, event_type='Remove from cart', description=f'{product_name} removed from cart')
            db.session.add(audit_record)
            db.session.commit()

           
            # Return a success message
            return jsonify({"message": "Product removed from cart successfully","totalPrice": updated_total_price})
        else:
            # Product not found
            return jsonify({"message": "Product not found in cart"})
    except Exception as e:
        # Handle any potential errors
        return jsonify({"message": "Error: " + str(e)})
    
def get_cart_total():
    
    total_price = db.session.query(func.sum(cart.price)).scalar()
    return total_price if total_price else 0.0

# END OF FUNCTIONS FOR CART

#get the total price of all items in the cart
@app.route("/get-total-price", methods=["GET"])
def get_total_price():
    user_id = session["user_id"]
    user_cart = cart.query.filter_by(customer_id=user_id).all()
    total_price = sum(item.total_price for item in user_cart)
    return jsonify({"total_price": total_price})

# REGISTRATION, FORGET PASS, AND LOGIN
@app.route("/signup", methods=["GET", "POST"])
def SignUp():
    error = None
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        username = request.form["username"]
        email = request.form["email"]
        account_type = request.form["accountType"]
        password = request.form["password"]

        if accounts.query.filter_by(email=email).first():
            error = "Email already exists. Please choose another email."
        else:
            # Hash the password before saving it
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

            # Create a new Account object with the hashed password and insert it into the database
            new_account = accounts(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                account_type=account_type,
                password=hashed_password,  # Use the hashed password
            )
            db.session.add(new_account)
            db.session.commit()

    return render_template("signup.html", error=error)



def send_reset_email(email):
    user = accounts.query.filter_by(email=email).first()

    if user:
        token = user.get_reset_token()
        user.reset_token = token
        db.session.commit()

        # Update the URL to use the correct endpoint and token value
        reset_url = url_for('ResetPassword', token=token, email=email, _external=True)

        msg = Message('Password Reset Request',
                      sender=user.email,
                      recipients=[user.email])
        msg.body = f'''To reset your password, visit the following link:
    {reset_url}

    If you did not make this request then simply ignore this email and no changes will be made.
    '''
        mail.send(msg)


@app.route("/forgot-password", methods=['GET', 'POST'])
def ForgotPassword():
    form = ForgotPasswordForm()
    error = None

    if form.validate_on_submit():
        user = accounts.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(form.email.data)
            flash('Reset instructions sent to your email.', 'success')
        else:
            error = "Invalid email. Please check and try again."
    
    return render_template('forgot_password.html', form=form, error=error)



    


@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def ResetPassword(token):
    # Rest of the code...
    user = accounts.query.filter_by(reset_token=token).first()

    if not user:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('ForgotPassword'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('ResetPassword', token=token))

        # Set the new password in the user object
        user.password = generate_password_hash(new_password)
        user.reset_token = None  # Reset the reset_token field after password change
        db.session.commit()

        flash('Your password has been updated! You can now log in with your new password.', 'success')
        return redirect(url_for('Login'))

    return render_template('reset_password.html', title='Reset Password', token=token)

    


# END OF REGISTRATION, FORGET PASS, AND LOGIN

# CUSTOMERS
@app.route("/product-info/<int:product_id>")
def ProductInfo(product_id):
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
    else:
        # User is not logged in, or no cart data found
        cart_count = 0
   
    product = Product.query.get(product_id)

    seller_id = product.seller_id
    seller = accounts.query.get(seller_id)
    if product is not None:
        product.product_image = b64encode(product.product_image).decode("utf-8")
        return render_template("customers/product_info_page.html", cart_count=cart_count, product=product, seller=seller)
    else:
        # Handle the case where the product does not exist

        return redirect(url_for("CampingHikingGear"))


@app.route("/track-order")
def trackorder():
    return render_template("Customers/order_tracking.html")

    
@app.route("/my-orders")
def MyOrder():
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_order = customerOrders.query.filter_by(customer_id=user_id).all()
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)

        for order in user_order:
            order.product_image = b64encode(order.product_image).decode("utf-8")
        return render_template(
            "/customers/my_orders_page.html",
            orders=user_order,   cart_count=cart_count
            

        )
    else:
        # User is not logged in
        return render_template(
            "customers/cart.html", products=[], cart_count=0
        )


#place order
@app.route("/one_place_order", methods=['POST'])
def one_place_order():
   if request.method == 'POST':
        product_id = request.json.get('productId')
        customer_id = session.get('user_id')

        # Retrieve product details from the database based on product_id
        product = Product.query.get(product_id)
        seller_id = product.seller_id
        seller = accounts.query.get(seller_id)
        # Create a new order record
        new_order = Orders(
            customer_id=customer_id,
            seller_name=seller.username,  # Replace with actual seller name
            product_name=product.product_name,
            product_details=product.product_details,
            product_image=product.product_image,
            mime_type=product.mime_type,
            category=product.category,
            price=product.price,
            quantity=1,  # Assuming a quantity of 1 for simplicity
            total=product.price,  # Assuming total is the same as price for simplicity
        )

        # Add the new order to the database
        db.session.add(new_order)
               

        customer = db.session.query(accounts).get(customer_id)
        customer_username = customer.username if customer else "Unknown"
        # Create a new order record
        customer_order = customerOrders(
            product_image=product.product_image,
            mime_type=product.mime_type,
            seller_id=seller.id, 
            customer_id=customer_id,
            customer_name=customer_username, 
            product_name=product.product_name,
            status='preparing', 
            product_details=product.product_details,
            orderdate=datetime.utcnow(),
            price=product.price,
            quantity=1, 
            total=product.price,  
            category=product.category,
        )
        db.session.add(customer_order)
        db.session.commit()

        return jsonify({'message': 'Order placed successfully'})
   else:
        return jsonify({'message': 'Invalid request method'})

@app.route("/place_order", methods=['POST'])
def place_order():
    if request.method == 'POST':
        product_ids = request.json.get('productIds', [])
        customer_id = session['user_id']
    
        for product_id in product_ids:
            # Retrieve product details from the database based on product_id
            product = cart.query.get(product_id)
            
            seller_id = product.seller_id
            seller = accounts.query.get(seller_id)

            # Create a new order record
            new_order = Orders(
                customer_id=customer_id,
                seller_name=seller.username,  # Replace with actual seller name
                product_name=product.product_name,
                product_details=product.description,
                product_image=product.product_image,
                mime_type=product.mime_type,
                category=product.category,
                price=product.price,
                quantity=1,  # Assuming a quantity of 1 for simplicity
                total=product.price,  # Assuming total is the same as price for simplicity
            )

            # Add the new order to the database
            db.session.add(new_order)
            db.session.delete(product)
            
            customer = db.session.query(accounts).get(customer_id)
            customer_username = customer.username if customer else "Unknown"
        # Create a new order record
            customer_order = customerOrders(
                product_image=product.product_image,
                mime_type=product.mime_type,
                seller_id=seller.id, 
                customer_id=customer_id,
                customer_name=customer_username, 
                product_name=product.product_name,
                status='preparing', 
                product_details=product.description,
                orderdate=datetime.utcnow(),
                price=product.price,
                quantity=1, 
                total=product.price,  
                category=product.category,
        )
            db.session.add(customer_order)
            db.session.commit()
            

        return jsonify({'message': 'Order placed successfully'})
    else:
        return jsonify({'message': 'Invalid request method'})
# CHECKOUT
@app.route("/customers/cart")
def Cart():
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)

        for product in user_cart:
            product.product_image = b64encode(product.product_image).decode("utf-8")
        return render_template(
            "/customers/cart.html",
            products=user_cart,
            cart_count=cart_count,

        )
    else:
        # User is not logged in
        return render_template(
            "customers/cart.html", products=[], cart_count=0
        )


@app.route("/checkout/<int:product_id>")
def buyNow(product_id):
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
    else:
        # User is not logged in, or no cart data found
        cart_count = 0

    # Fetch the selected product
    product = Product.query.get(product_id)

    if product is not None:
        product.product_image = b64encode(product.product_image).decode("utf-8")
        return render_template("customers/one_checkout_page.html", cart_count=cart_count, products=[product])
    else:
        # Handle the case where the product does not exist
   
        return redirect(url_for("CampingHikingGear"))


@app.route("/customers/checkout")
def checkout():
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
        total_price = sum(product.price for product in user_cart)
        for product in user_cart:
            product.product_image = b64encode(product.product_image).decode("utf-8")
        return render_template(
            "customers/checkout_page.html",
            products=user_cart,
            cart_count=cart_count, total_price=total_price
       
        )
    else:
        # User is not logged in
        return render_template(
            "customers/checkout_page.html", products=[], cart_count=0
        )


@app.route("/customers/myprofile")
def MyProfile():
    return render_template("customers/my_profile.html")


@app.route("/customers/outdoor-clothing")
def OutdoorClothing():
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
    else:
        # User is not logged in, or no cart data found
        cart_count = 0
    outdoor_clothing_products = Product.query.filter_by(category="Outdoor Clothing").all()

    for product in outdoor_clothing_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")


    return render_template("customers/outdoor_clothing_page.html", cart_count=cart_count, outdoor_clothing=outdoor_clothing_products)
 


@app.route("/customers/exercise-and-fitness-gear")
def ExerciseFitnessGear():
    
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
    else:
        # User is not logged in, or no cart data found
        cart_count = 0
 
    exercise_fitness_gear_products = Product.query.filter_by(category="Exercise & Fitness Gear").all()

    for product in exercise_fitness_gear_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")
        
    return render_template("customers/exercise_and_fitness_gear_page.html", cart_count=cart_count,exercise_products=exercise_fitness_gear_products)

 


@app.route("/customers/sports-equipment")
def SportsEquipment():

    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
    else:
        # User is not logged in, or no cart data found
        cart_count = 0

    sports_equipment_products = Product.query.filter_by(category="Sports Equipment").all()
    
    for product in sports_equipment_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")

    return render_template("customers/sports_equipment_page.html", cart_count=cart_count, sports_products=sports_equipment_products)



@app.route("/customers/camping-and-hiking-gear")
def CampingHikingGear():
     if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
     else:
        # User is not logged in, or no cart data found
        cart_count = 0

     camping_hiking_gear_products = Product.query.filter_by(category="Camping & Hiking Gear").all()
     for product in camping_hiking_gear_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")


     return render_template("customers/camping_and_hiking_gear_page.html", cart_count=cart_count,camping_products=camping_hiking_gear_products)



# END OF CUSTOMERS


# SELLERS

@app.route('/update_order_status/<int:order_id>/<new_status>', methods=['POST'])
def update_order_status(order_id, new_status):
    order = customerOrders.query.get_or_404(order_id)
    order.status = new_status
    db.session.commit()
    return jsonify({'success': True})




@app.route("/seller/dashboard")
def SellerDashboard():
    seller_id = session.get('user_id')

    if seller_id is not None:
        # Fetch orders based on the seller_id
        orders = customerOrders.query.filter_by(seller_id=seller_id).all()


    
    
        for product in orders:
            product.product_image = b64encode(product.product_image).decode("utf-8")
        
    return render_template("sellers/seller_dashboard.html",orders=orders)


@app.route("/seller/courier")
def Courier():
    return render_template("sellers/courier.html")


@app.route("/seller/addproducts", methods=['GET', 'POST'])
def AddProducts():
    seller_id = None  # Initialize seller_id to None
    if "user_id" in session:
       seller_id = session["user_id"]
       if request.method == 'POST':
    
        product_name = request.form['productName']
        product_details = request.form['productDetails']
        
           # Handle the SVG image data
        product_image_file = request.files['productImage']
        product_image = product_image_file.read()
        mime_type = product_image_file.content_type
        
    
        mime_type = request.files['productImage'].content_type
        category = request.form['productCategory']
        price = request.form['productPrice']
        quantity = request.form['productQuantity']

        new_product = Product(
            seller_id=seller_id,
            product_name=product_name,
            product_details=product_details,
            product_image=product_image,
            mime_type=mime_type,
            category=category,
            price=price,
            quantity=quantity,
           
        )
      
        db.session.add(new_product)
        db.session.commit()
    if seller_id is not None:
        # Retrieve and decode the product images
        products = Product.query.filter_by(seller_id=seller_id).all()
        for product in products:
            product.product_image = base64.b64encode(product.product_image).decode("utf-8")
    else:
        products = []  
        
    return render_template("sellers/add_products.html", seller_products=products)


#Rating
@app.route('/store_rating', methods=['POST'])
def store_rating():
    data = request.get_json()
    order_id = data.get('orderId')
    rating_value = data.get('rating')

    try:
        # Find the product based on the order_id
        product = Product.query.filter_by(id=order_id).first()

        if product:
            # Check if the user has already rated this product (you might want to add more logic here)
            # For simplicity, let's assume a user can rate a product only once
            # You might want to link this to a user in your system      
            user_id = session["user_id"]  # Replace with the actual user ID

            existing_rating = Rating.query.filter_by(product_id=order_id, user_id=user_id).first()

            if existing_rating:
                return jsonify({'error': 'You have already rated this product'})

            # Create a new rating
            new_rating = Rating(product_id=order_id, user_id=user_id, rating=rating_value)

            # Save the new rating to the database
            db.session.add(new_rating)
            db.session.commit()

            return jsonify({'message': 'Rating stored successfully'})
        else:
            return jsonify({'error': 'Product not found'})

    except Exception as e:
        # Handle exceptions based on your specific requirements
        return jsonify({'error': str(e)})


@app.route("/seller/viewtransactions")
def Transactions():
    return render_template("sellers/view_transactions.html")


@app.route("/seller/inventory")
def Inventory():
    return render_template("sellers/inventory.html")


@app.route("/seller/accounting")
def Accounting():
    return render_template("sellers/accounting.html")


# END OF SELLERS


# ADMIN
@app.route("/admin/admin-dashboard")
def AdminDashboard():
    total_users = accounts.query.count()
    return render_template("administrator/dashboard.html", total_users=total_users)

def get_paginated_user_products(page, per_page, user_id):
    product = Product.query.filter_by(seller_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
    return product

@app.route('/user/<int:user_id>')
def User(user_id):
    page = request.args.get('page', default=1, type=int)
    per_page = 5
    user_products = get_paginated_user_products(page, per_page, user_id)
    user = accounts.query.get_or_404(user_id)
    
   

    return render_template('administrator/specUser.html', user=user, user_products=user_products, user_id=user_id)


#for pagination
def get_paginated_users(page, per_page):
    products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    return products

@app.route("/admin/users")
def Users():

    page = request.args.get('page', default=1, type=int)
    per_page =5
    users = get_paginated_users(page, per_page)
    search_term = request.args.get('search', default='', type=str)

      # Query users matching the search term
    users = accounts.query.filter(accounts.email.ilike(f"%{search_term}%")).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("administrator/user.html",users=users, searchTerm=search_term)


#audit trail pagination
def get_paginated_audit_trail(page, per_page):
    activities = auditTrail.query.paginate(page=page, per_page=per_page, error_out=False)
    return activities

@app.route('/audit-trail')
def AuditTrail():
    page = request.args.get('page', default=1, type=int)
    per_page =5
    audit_records = get_paginated_audit_trail(page, per_page)
   

    return render_template('/administrator/auditTrail.html',audit_records=audit_records)


@app.route("/admin/cashout-request")
def CashoutRequest():
    return render_template("administrator/cashoutRequest.html")


@app.route("/admin/system-balance")
def SystemBalance():
    return render_template("administrator/systemBalance.html")


@app.route("/admin/specific-user-transaction")
def SpecificUserTransaction():
    return render_template("administrator/specUserTransaction.html")


@app.route("/admin/specific-user-audit-trail")
def SpecificUserAuditTrail():
    return render_template("administrator/userAuditTrail.html")

#suspend user
@app.route("/suspend-user", methods=["POST"])
def suspend_user():

    user_id_to_suspend = request.form.get("user_id")
    if user_id_to_suspend:
        user = accounts.query.get(user_id_to_suspend)

        if user:
            # Toggle the suspension status
            user.is_suspended = not user.is_suspended
            db.session.commit()

            # Create an audit trail record for the suspension
            email = session["user_email"]  # Assuming the admin's email is in the session
            audit_record = auditTrail(user=email, event_type='Suspend User', description=f'Suspended user with ID: {user.id}')
            db.session.add(audit_record)
            db.session.commit()

            # Redirect back to the admin page or another appropriate destination
            return redirect(url_for("admin_dashboard"))
    
    return "Invalid user or unauthorized access"  # You can customize this message or redirect to an error page

# END OF ADMIN

if __name__ == "__main__":
    app.run(debug=True)
