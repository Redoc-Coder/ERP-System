import os
from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    session,
    request,
    jsonify,
)

from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from models import db, accounts, cart, auditTrail
from sqlalchemy.sql import func
from base64 import b64encode
import base64

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "my_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "db.sqlite3"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"

db.init_app(app)


# FUNCTIONS FOR LOGIN
@app.route("/login", methods=["GET", "POST"])
def Login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Query the database for a user with the given username
        user = accounts.query.filter_by(email=username).first()
    
        if user and user.password == password:
            
            session["user_id"] = user.id
            session["user_email"] = user.email
            audit_record = auditTrail(user=username, event_type='Login', description='User logged in')
            db.session.add(audit_record)
            db.session.commit()
            return redirect(
                url_for("LandingPage")
            )  

        else:
            error = "Invalid email or password. Please try again."

    return render_template("login.html", error=error)


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

    return render_template("customers/landingpage.html", cart_count=cart_count)


# END OF FUNCTIONS LOGIN


# FUNCTIONS FOR CART
@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    product_name = request.form["product_name"]
    product_price = request.form["product_price"]

    # You can directly read the image file from the server
    image_file_path = "static/images/trail_running_shoes.jpg"
    with open(image_file_path, "rb") as image_file:
        product_image = image_file.read()

    # Get the user ID from the session
    user_id = session.get("user_id")

    # Insert the product information into the cart table, associating it with the user
    new_cart_item = cart(
        customer_id=user_id,
        seller_id=1,  # Replace with the actual seller ID
        product_name=product_name,
        price=product_price,
        product_image=product_image,
        quantity=1,
        total_price=product_price,
        mime_type="image/jpeg",  # Set the appropriate MIME type
        category="basta",
    )
    
    db.session.add(new_cart_item)
  
    #add data to audit trail
    email = session["user_email"]
    audit_record = auditTrail(user=email, event_type='Add to cart', description=f'Product: {product_name}')
    db.session.add(audit_record)
    db.session.commit()

    response = {"message": "Product added to cart successfully"}
    return jsonify(response)


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
             # Add record for audit trail
            email = session["user_email"]
            audit_record = auditTrail(user=email, event_type='Remove from cart', description=f'{product_name} removed from cart')
            db.session.add(audit_record)
            db.session.commit()

           
            # Return a success message
            return jsonify({"message": "Product removed from cart successfully"})
        else:
            # Product not found
            return jsonify({"message": "Product not found in cart"})
    except Exception as e:
        # Handle any potential errors
        return jsonify({"message": "Error: " + str(e)})

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
            # Create a new Account object and insert it into the database
            new_account = accounts(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                account_type=account_type,
                password=password,
            )
            db.session.add(new_account)
            db.session.commit()

    return render_template("signup.html", error=error)


@app.route("/forgot-password")
def ForgotPassword():
    return render_template("forgot_password.html")


@app.route("/reset-password")
def ResetPassword():
    return render_template("reset_password.html")


# END OF REGISTRATION, FORGET PASS, AND LOGIN

# CUSTOMERS
@app.route("/product-info")
def ProductInfo():
    return render_template("customers/product_info_page.html")


# CHECKOUT
@app.route("/customers/cart")
def Cart():
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
        total_price = sum(item.total_price for item in user_cart)
        for product in user_cart:
            product.product_image = b64encode(product.product_image).decode("utf-8")
        return render_template(
            "/customers/cart.html",
            products=user_cart,
            cart_count=cart_count,
            total_price=total_price,
        )
    else:
        # User is not logged in
        return render_template(
            "customers/cart.html", products=[], cart_count=0, total_price=0
        )



@app.route("/customers/checkout")
def checkout():
    if "user_id" in session:
        # User is logged in
        user_id = session["user_id"]
        user_cart = cart.query.filter_by(customer_id=user_id).all()
        cart_count = len(user_cart)
        total_price = sum(item.total_price for item in user_cart)
        for product in user_cart:
            product.product_image = b64encode(product.product_image).decode("utf-8")
        return render_template(
            "customers/checkout_page.html",
            products=user_cart,
            cart_count=cart_count,
            total_price=total_price,
        )
    else:
        # User is not logged in
        return render_template(
            "customers/checkout_page.html", products=[], cart_count=0, total_price=0
        )


@app.route("/customers/myprofile")
def MyProfile():
    return render_template("customers/my_profile.html")


@app.route("/customers/outdoor-clothing")
def OutdoorClothing():
    return render_template("customers/outdoor_clothing_page.html")


@app.route("/customers/exercise-and-fitness-gear")
def ExerciseFitnessGear():
    return render_template("customers/exercise_and_fitness_gear_page.html")


@app.route("/customers/sports-equipment")
def SportsEquipment():
    return render_template("customers/sports_equipment_page.html")


@app.route("/customers/camping-and-hiking-gear")
def CampingHikingGear():
    return render_template("customers/camping_and_hiking_gear_page.html")


# END OF CUSTOMERS


# SELLERS
@app.route("/seller/dashboard")
def SellerDashboard():
    return render_template("sellers/seller_dashboard.html")


@app.route("/seller/courier")
def Courier():
    return render_template("sellers/courier.html")


@app.route("/seller/addproducts")
def AddProducts():
    return render_template("sellers/add_products.html")


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


@app.route("/admin/user", methods=["GET", "POST"])
def User():
    if request.method == "POST":
        user_id_to_suspend = request.form.get("user_id")
        if user_id_to_suspend:
            user = accounts.query.get(user_id_to_suspend)
            if user:
                # Toggle the suspension status
                user.is_suspended = not user.is_suspended
                db.session.commit()

                # Create an audit trail record for the suspension
                email = session["user_email"]  # Assuming the admin's email is in the session
                audit_record = auditTrail(user=email, event_type='Suspend User', description=f'Admin suspended the user with ID: {user.id}')
                db.session.add(audit_record)
                db.session.commit()

    # Your existing admin page logic
    return render_template("administrator/specUser.html")  # Include the list of users or user data


#for pagination
def get_paginated_users(page, per_page):
    users = accounts.query.paginate(page=page, per_page=per_page, error_out=False)
    return users

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
