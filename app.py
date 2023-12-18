import os
from flask import (
    Flask,
    render_template,
    url_for,
    redirect,
    session,
    request,
    jsonify, flash
)

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_mail import Mail, Message
from wtforms.validators import Email as EmailValidator
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.sql import func
from base64 import b64encode
import base64
from models import db, accounts, cart, auditTrail, Product, Orders, customerOrders, Rating, DisabledProduct

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

        if username == 'admin@gmail.com' and password == 'admin':
            
            return redirect(url_for("AdminDashboard"))

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
        user = accounts.query.all()  
        user_image = accounts.query.get(user_id)
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
    else:
        
        cart_count = 0

    outdoor_clothing_products = Product.query.filter_by(category="Outdoor Clothing").all()
    exercise_fitness_gear_products = Product.query.filter_by(category="Exercise & Fitness Gear").all()
    camping_hiking_gear_products = Product.query.filter_by(category="Camping & Hiking Gear").all()
    sports_equipment_products = Product.query.filter_by(category="Sports Equipment").all()

    top_products = Product.query.order_by(desc(Product.sold)).limit(4).all()



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

    if user_image:
        user_image.profile = b64encode(user_image.profile).decode("utf-8")

    return render_template(
        "customers/landingpage.html",
        cart_count=cart_count,
        outdoor_clothing=outdoor_clothing_products,
        exercise_products=exercise_fitness_gear_products,
        camping_products=camping_hiking_gear_products,
        sports_products=sports_equipment_products,
        calculate_average_rating=calculate_average_rating,
        user_image=user_image, top_products = top_products
    )



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

            # Check if the product is already in the cart
            existing_cart_item = cart.query.filter_by(customer_id=customer_id, product_id=product.id).first()
            if existing_cart_item:
                return jsonify({'error': 'Product already in cart'})

            new_product = cart(
                customer_id=customer_id,
                seller_id=seller_id,
                shop_name=shop_name,
                product_id=product.id,
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

        password = request.form["password"]

        if accounts.query.filter_by(email=email).first():
            error = "Email already exists. Please choose another email."
        else:

            with open('static/images/defulat_image.jpg', 'rb') as image_file:
                default_image = image_file.read()
            # Hash the password before saving it
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

            # Create a new Account object with the hashed password and insert it into the database
            new_account = accounts(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                account_type='seller/buyer',
                password=hashed_password,
                mime_type='image/jpeg'  # Use the hashed password
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
         
        user_image = accounts.query.get(user_id)
        products = Product.query.all()
        for product in products:
            product.average_rating = calculate_average_rating(product)
        


    else:
        # User is not logged in, or no cart data found
        cart_count = 0
   
    product = Product.query.get(product_id)
    
    related_products = Product.query.filter(Product.category == product.category, Product.id != product_id).all()
            
    seller_id = product.seller_id
    seller = accounts.query.get(seller_id)
    num_ratings = Rating.query.filter_by(product_id=product_id).count()

    for r_product in related_products:
        r_product.product_image = b64encode(r_product.product_image).decode("utf-8")
       


    if product is not None:
        product.product_image = b64encode(product.product_image).decode("utf-8")
        user_image.profile = b64encode(user_image.profile).decode("utf-8")
        
    
        return render_template("customers/product_info_page.html", cart_count=cart_count, product=product, seller=seller, num_ratings=num_ratings, 
                               related_products=related_products, user_image=user_image, calculate_average_rating = calculate_average_rating)
    else:
        # Handle the case where the product does not exist

        return redirect(url_for("CampingHikingGear"))


@app.route("/track-order")
def trackorder():
    return render_template("Customers/order_tracking.html")

    
@app.route("/my-orders", methods=['GET', 'POST'])
def MyOrder():
    if "user_id" in session:
        user_id = session["user_id"]
        user_order = customerOrders.query.filter_by(customer_id=user_id).all()
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
        user = accounts.query.all() 
        user_image = accounts.query.get(user_id)
        
        
        # Fetch the ratings for the user
        # Fetch the ratings for the specific user and products
        user_ratings = Rating.query.filter(Rating.user_id == user_id, Rating.product_id.in_([order.product_id for order in user_order])).all()

        # Attach ratings to the corresponding orders
        for order in user_order:
            matching_rating = next((rating for rating in user_ratings if rating.product_id == order.product_id), None)
            order.user_rating = matching_rating.rating if matching_rating else 0

        for order in user_order:
            order.product_image = b64encode(order.product_image).decode("utf-8")
        if user_image:
            user_image.profile = b64encode(user_image.profile).decode("utf-8")

        if request.method == 'POST':
             return redirect(url_for('MyOrder'))

   

        return render_template(
            "/customers/my_orders_page.html",
            orders=user_order, cart_count=cart_count,user_image=user_image
        )
    else:
        return render_template("customers/cart.html", products=[], cart_count=0,user_image=user_image,)

@app.route("/cancel_order/<int:order_id>", methods=['POST'])
def cancel_order(order_id):
    order = customerOrders.query.get(order_id)
    if order:
        # Update the order status to 'cancelled'
        order.status = 'cancelled'
        db.session.commit()
    return redirect(url_for('MyOrder'))

#place order
@app.route("/one_place_order", methods=['POST'])
def one_place_order():
   if request.method == 'POST':
        product_id = request.json.get('productId')
        customer_id = session.get('user_id')
        address = request.json.get('address')  # Get the address value
        payment_method = request.json.get('paymentMethod')  # Get the payment method value
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
            quantity=product.order_quantity,  
            total=product.price*product.order_quantity,  
            address=address,
            payment_method=payment_method
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
            product_id =product.id,
            product_name=product.product_name,
            status='placed', 
            product_details=product.product_details,
            orderdate=datetime.utcnow(),
            price=product.price,
            quantity=product.order_quantity, 
            total=product.price*product.order_quantity,  
            category=product.category,
            address=address,
            payment_method=payment_method
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
        address = request.json.get('address')  # Get the address value
        payment_method = request.json.get('paymentMethod')  # Get the payment method value
        for product_id in product_ids:
            # Retrieve product details from the database based on product_id
            product = cart.query.get(product_id)
            
            seller_id = product.seller_id
            seller = accounts.query.get(seller_id)

            # Create a new order record
            new_order = Orders(
                customer_id=customer_id,
                seller_name=seller.username,
                product_name=product.product_name,
                product_details=product.description,
                product_image=product.product_image,
                mime_type=product.mime_type,
                category=product.category,
                price=product.price,
                quantity=product.quantity,  
                total=product.price*product.quantity,  
                address=address,
                payment_method=payment_method
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
                product_id = product.product_id,
                product_name=product.product_name,
                status='placed', 
                product_details=product.description,
                orderdate=datetime.utcnow(),
                price=product.price,
                quantity=product.quantity, 
                total=product.price,  
                category=product.category,
                address=address,
                payment_method=payment_method   
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
        user = accounts.query.all() 
        user_image = accounts.query.get(user_id)
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)

        for product in user_cart:
            product.product_image = b64encode(product.product_image).decode("utf-8")

        
        for user_image in user:
            user_image.profile = b64encode(user_image.profile).decode("utf-8")
        return render_template(
            "/customers/cart.html",user_image=user_image,
            products=user_cart,
            cart_count=cart_count,

        )
    else:
        # User is not logged in
        return render_template(
            "customers/cart.html", products=[], cart_count=0
        )

#Update quantity
@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    data = request.get_json()
    product_id = data['productId']
    new_quantity = data['newQuantity']

    # Update the quantity in the database
    product = cart.query.get(product_id)
    product.quantity = new_quantity
    db.session.commit()

    return jsonify({'message': 'Quantity updated successfully'})

#solo product update
@app.route('/update_order_quantity', methods=['POST'])
def update_order_quantity():
    data = request.get_json()
    product_id = data['productId']
    new_order_quantity = data['newOrderQuantity']

    # Update the order_quantity in the Product table
    product = Product.query.get(product_id)

    # Check if the product exists
    if product:
        product.order_quantity = new_order_quantity
        db.session.commit()
        return jsonify({'message': 'Order quantity updated successfully'})
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route("/checkout/<int:product_id>")
def buyNow(product_id):
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
        user_image = accounts.query.get(user_id)
        
    else:
        # User is not logged in, or no cart data found
        cart_count = 0

    # Fetch the selected product
    product = Product.query.get(product_id)
    total_price = product.price * product.order_quantity
    if user_image:
            user_image.profile = b64encode(user_image.profile).decode("utf-8")

    if product is not None:
        product.product_image = b64encode(product.product_image).decode("utf-8")
        return render_template("customers/one_checkout_page.html", cart_count=cart_count, products=[product], user_image = user_image,
        total_price = total_price)
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
        total_price = sum(product.price * product.quantity for product in user_cart)
        user_image = accounts.query.get(user_id)

        if user_image:
            user_image.profile = b64encode(user_image.profile).decode("utf-8")
        for product in user_cart:
            product.product_image = b64encode(product.product_image).decode("utf-8")
        
        return render_template(
            "customers/checkout_page.html",
            products=user_cart,
            cart_count=cart_count, total_price=total_price,user_image=user_image
       
        )
    else:
        # User is not logged in
        return render_template(
            "customers/checkout_page.html", products=[], cart_count=0
        )


@app.route("/customers/myprofile")
def MyProfile():
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        all_user = accounts.query.all()
        user = accounts.query.get(user_id)
        user_image = accounts.query.get(user_id)
        cart_count = len(user_cart)
    else:
        # User is not logged in, or no cart data found
        cart_count = 0
        user = None
    if user_image:
        user_image.profile = b64encode(user_image.profile).decode("utf-8")
    return render_template("customers/my_profile.html",cart_count=cart_count, user=user,user_image=user_image)

# Update profile
@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" in session:
        user_id = session["user_id"]
        user = accounts.query.get(user_id)

        # Update user details
        user.firstname = request.form.get("firstname")
        user.lastname = request.form.get("lastname")
        user.email = request.form.get("email")
        user.address = request.form.get("address")

        # Handle file upload
        profile_image = request.files.get("profile_image")
        if profile_image:
            user.profile = profile_image.read()
            user.mime_type = profile_image.mimetype

        # Update password if provided
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password == confirm_password:
            user.password = generate_password_hash(new_password)
            db.session.commit()
        else:
            flash("Passwords do not match", "error")  # You can use Flask's flash to display error messages

    return redirect(url_for("MyProfile"))

@app.route("/customers/outdoor-clothing")
def OutdoorClothing():
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user = accounts.query.all() 
        user_image = accounts.query.get(user_id)
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
        products = Product.query.all()
        for product in products:
            product.average_rating = calculate_average_rating(product)
    else:
        # User is not logged in, or no cart data found
        cart_count = 0
    outdoor_clothing_products = Product.query.filter_by(category="Outdoor Clothing").all()

    for product in outdoor_clothing_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")
    if user_image:
        user_image.profile = b64encode(user_image.profile).decode("utf-8")

    return render_template("customers/outdoor_clothing_page.html",user_image=user_image, cart_count=cart_count, outdoor_clothing=outdoor_clothing_products)
 


@app.route("/customers/exercise-and-fitness-gear")
def ExerciseFitnessGear():
    
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user = accounts.query.all() 
        user_image = accounts.query.get(user_id)
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
        products = Product.query.all()
        for product in products:
            product.average_rating = calculate_average_rating(product)
    else:
        # User is not logged in, or no cart data found
        cart_count = 0
 
    exercise_fitness_gear_products = Product.query.filter_by(category="Exercise & Fitness Gear").all()

    for product in exercise_fitness_gear_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")

    if user_image:
        user_image.profile = b64encode(user_image.profile).decode("utf-8")

        
    return render_template("customers/exercise_and_fitness_gear_page.html",user_image=user_image, cart_count=cart_count,exercise_products=exercise_fitness_gear_products)

 


@app.route("/customers/sports-equipment")
def SportsEquipment():

    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user = accounts.query.all() 
        user_image = accounts.query.get(user_id)
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
        products = Product.query.all()
        for product in products:
            product.average_rating = calculate_average_rating(product)
    else:
        # User is not logged in, or no cart data found
        cart_count = 0

    sports_equipment_products = Product.query.filter_by(category="Sports Equipment").all()
    
    for product in sports_equipment_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")
    if user_image:
        user_image.profile = b64encode(user_image.profile).decode("utf-8")


    return render_template("customers/sports_equipment_page.html", user_image=user_image,cart_count=cart_count, sports_products=sports_equipment_products)



@app.route("/customers/camping-and-hiking-gear")
def CampingHikingGear():
     if "user_id" in session:
        # User is logged in
        user = accounts.query.all() 
        user_id = session["user_id"]
        user_image = accounts.query.get(user_id)
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
        products = Product.query.all()
        for product in products:
            product.average_rating = calculate_average_rating(product)
     else:
        # User is not logged in, or no cart data found
        cart_count = 0

     camping_hiking_gear_products = Product.query.filter_by(category="Camping & Hiking Gear").all()
     for product in camping_hiking_gear_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")

     if user_image:
        user_image.profile = b64encode(user_image.profile).decode("utf-8")



     return render_template("customers/camping_and_hiking_gear_page.html", user_image=user_image,cart_count=cart_count,camping_products=camping_hiking_gear_products)



# END OF CUSTOMERS


# SELLERS

@app.route('/update_order_status/<int:order_id>/<new_status>', methods=['POST'])
def update_order_status(order_id, new_status):
    order = customerOrders.query.get_or_404(order_id)

    # Check if the status is being updated to 'delivered'
    if new_status.lower() == 'delivered':
        # Increment the 'sold' column in the associated product
        product = Product.query.join(customerOrders, Product.id == customerOrders.product_id).filter(customerOrders.id == order_id).first()

        if product:
            product.sold += order.quantity
            product.quantity-=order.quantity
            db.session.commit()

                        
            seller_account = accounts.query.get_or_404(product.seller_id)
            seller_account.sales += (order.quantity * product.price)
            db.session.commit()

    order.status = new_status
    db.session.commit()

    return jsonify({'success': True})




myChart1 = None

# Route to render the seller dashboard with the chart and top sellers data
@app.route("/seller/dashboard")
def SellerDashboard():
    

    seller_id = session.get('user_id')

    if seller_id is not None:
        # Fetch orders based on the seller_id
        orders = customerOrders.query.filter_by(seller_id=seller_id).all()
        seller = accounts.query.get_or_404(seller_id)
        total_sales = seller.sales
        total_products = Product.query.filter_by(seller_id=seller_id).count()
        delivered_orders = customerOrders.query.filter_by(seller_id=seller_id, status='delivered').all()
        total_delivered_orders = len(delivered_orders)



        for product in orders:
            product.product_image = b64encode(product.product_image).decode("utf-8")

        # Fetch top sellers data from the database


    return render_template("sellers/seller_dashboard.html",
                           orders=orders,
                           total_sales=total_sales,
                           total_products=total_products,
                           total_delivered_orders=total_delivered_orders)






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
        disabled_products = DisabledProduct.query.filter_by(seller_id=seller_id).all()
        for product in products:
            product.product_image = base64.b64encode(product.product_image).decode("utf-8")
        for product in disabled_products:
            product.product_image = base64.b64encode(product.product_image).decode("utf-8")
    else:
        products = []  
        
    return render_template("sellers/add_products.html", seller_products=products, disabled_products=disabled_products)

#archive seller product

@app.route('/delete_product_ajax/<int:product_id>', methods=['POST'])
def delete_product_ajax(product_id):
    product = Product.query.get_or_404(product_id)

    try:
        # Check if the product has any ratings
        if product.num_ratings() > 0:
            # Remove the ratings associated with the product
            ratings = Rating.query.filter_by(product_id=product_id).all()
            for rating in ratings:
                db.session.delete(rating)

        # Create a disabled product using the attributes of the original product
        disabled_product = DisabledProduct(
            product_name=product.product_name,
            product_details=product.product_details,
            product_image=product.product_image,
            mime_type=product.mime_type,
            category=product.category,
            price=product.price,
            quantity=product.quantity,
            seller_id=product.seller_id,
            deleted_at=datetime.now()
        )

        # Add the disabled product to the database
        db.session.add(disabled_product)

        # Delete the original product
        db.session.delete(product)
        
        db.session.commit()
        response = {'status': 'success', 'message': f'The product "{product.product_name}" has been deleted.'}
    except Exception as e:
        db.session.rollback()
        response = {'status': 'error', 'message': f'Error deleting the product: {str(e)}'}

    return jsonify(response)
#seller edit product

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/update_product/<int:product_id>", methods=["POST"])
def update_product(product_id):
    if "user_id" in session:
        user_id = session["user_id"]
        user = accounts.query.get(user_id)

        # Assuming you have a Product model
        product = Product.query.get_or_404(product_id)

        # Update product details
        product.product_name = request.form.get("product_name")
        product.product_details = request.form.get("product_details")
        product.category = request.form.get("category")

# Check if price and quantity are provided before converting
        price = request.form.get("price")
        quantity = request.form.get("quantity")

        if price is not None:
            product.price = float(price)

        if quantity is not None:
            product.quantity = int(quantity)

        # Handle file upload for product image
        product_image = request.files.get("product_image")
        if product_image and allowed_file(product_image.filename):
            product.product_image = product_image.read()
            product.mime_type = product_image.mimetype

        try:
            db.session.commit()
            flash("Product updated successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating product: {str(e)}", "error")

    return redirect(url_for("AddProducts", product_id=product_id))

@app.route('/add-product/<int:product_id>', methods=['POST'])
def add_product(product_id):
    try:
        # Get the disabled product from the database
        disabled_product = DisabledProduct.query.get_or_404(product_id)

        # Create a new product using the disabled product's data
        new_product = Product(
            seller_id=disabled_product.seller_id,
            product_name=disabled_product.product_name,
            product_details=disabled_product.product_details,
            product_image=disabled_product.product_image,
            mime_type=disabled_product.mime_type,
            category=disabled_product.category,
            price=disabled_product.price,
            quantity=disabled_product.quantity,

        )

        # Add the new product to the session and commit changes
        db.session.add(new_product)
        db.session.delete(disabled_product)
        db.session.commit()

        return jsonify({'message': 'Product successfully added'}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error adding product: {str(e)}")
        # Return an error response
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/store_rating', methods=['POST'])
def store_rating():
    # Check if the user is authenticated
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({'error': 'User not authenticated'})

    data = request.get_json()
    order_id = data.get('orderId')
    rating_value = data.get('rating')

    try:
        # Find the product based on the order_id
        product = Product.query.filter_by(id=order_id).first()

        if product:
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
    if "user_id" in session:
        user_id = session["user_id"]
        delivered_orders = customerOrders.query.filter(
    (customerOrders.seller_id == user_id) &
    ((customerOrders.status == 'delivered') | (customerOrders.status == 'cancelled'))
).all()
        return render_template("sellers/view_transactions.html", orders=delivered_orders)
    else:
        # Redirect to login or handle the case where the user is not logged in
        return redirect(url_for("login"))



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
    sales_data = db.session.query(Product.category, func.sum(Product.sold).label('total_sold')) \
        .group_by(Product.category) \
        .all()
    total_users = accounts.query.count()
    total_products = Product.query.count()
    total_accounts_sales = db.session.query(func.sum(accounts.sales)).scalar() or 0
    if sales_data:
        labels = [category for category, _ in sales_data]
        sales_quantities = [total_sold for _, total_sold in sales_data]
        top_sellers_data = accounts.query.order_by(accounts.sales.desc()).limit(3).all()

        for seller in top_sellers_data:
            seller.profile = b64encode(seller.profile).decode("utf-8")

    

        return render_template("administrator/dashboard.html", labels=labels, salesQuantities=sales_quantities, top_sellers_data=top_sellers_data
                               ,total_users=total_users, total_products=total_products, total_accounts_sales = total_accounts_sales)

    return render_template("administrator/dashboard.html", labels=[], salesQuantities=[], total_users=total_users,total_accounts_sales = total_accounts_sales)

# Route to provide JSON data for the chart
@app.route("/admin/admin-dashboard/data")
def getChartData():
    # Fetch actual sales data from the database
    sales_data = db.session.query(Product.category, func.sum(Product.sold).label('total_sold')) \
        .group_by(Product.category) \
        .all()
    
    

    if sales_data:
        labels = [category for category, _ in sales_data]
        sales_quantities = [total_sold for _, total_sold in sales_data]
        return jsonify(labels=labels, salesQuantities=sales_quantities)

    return jsonify(labels=[], salesQuantities=[])


# Define a function to update the chart with data
def updateChart(labels, salesQuantities):
    global myChart1  # Access the global variable
    myChart1.data.labels = labels
    myChart1.data.datasets[0].data = salesQuantities
    myChart1.update()


def get_paginated_user_products(page, per_page, user_id):
    product = Product.query.filter_by(seller_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
    return product

@app.route('/user/<int:user_id>')
def User(user_id):
    page = request.args.get('page', default=1, type=int)
    per_page = 5
    user_products = get_paginated_user_products(page, per_page, user_id)
    user = accounts.query.get_or_404(user_id)
    total_products = Product.query.filter_by(seller_id=user.id).count()
    delivered_orders = customerOrders.query.filter_by(seller_id=user.id, status='delivered').all()
    total_delivered_orders = len(delivered_orders)
    
    if user:
        user.profile = b64encode(user.profile).decode("utf-8")
    for product in user_products:
        product.product_image = b64encode(product.product_image).decode("utf-8")

    return render_template('administrator/specUser.html', user=user, user_products=user_products, user_id=user_id,
                           total_products = total_products, total_delivered_orders = total_delivered_orders)

@app.route('/remove-product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    try:
        # Get the product from the database
        product = Product.query.get_or_404(product_id)
        
        # Check if the product has any ratings
        if product.num_ratings() > 0:
            # Remove the ratings associated with the product
            ratings = Rating.query.filter_by(product_id=product_id).all()
            for rating in ratings:
                db.session.delete(rating)

        # Delete the product and commit changes
        db.session.delete(product)
        db.session.commit()

        # Redirect to the user's page after deletion
        return jsonify({'message': 'Product successfully removed'}), 200
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error removing product: {str(e)}")
        # Return an error response
        return jsonify({'error': 'Internal Server Error'}), 500

#for pagination
def get_paginated_users(page, per_page):
    products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    return products

@app.route("/admin/users")
def Users():

    page = request.args.get('page', default=1, type=int)
    per_page =7
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
    per_page =11
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


@app.route('/logout', methods=['POST'])
def logout():
    # Perform any necessary logout logic (e.g., clearing session data)
    session.clear()

    # You can return a JSON response if needed
    return jsonify({'message': 'Logout successful'})

# END OF ADMIN

if __name__ == "__main__":
    app.run(debug=True)
