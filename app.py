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
from models import db, accounts, cart
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


# functions for login
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
            return redirect(
                url_for("LandingPage")
            )  # Redirect to the dashboard or another page

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

    return render_template("landingpage.html", cart_count=cart_count)


# functions for cart
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

        if product_to_remove:
            # Remove the product from the cart
            db.session.delete(product_to_remove)
            db.session.commit()

            # Return a success message
            return jsonify({"message": "Product removed from cart successfully"})
        else:
            # Product not found
            return jsonify({"message": "Product not found in cart"})
    except Exception as e:
        # Handle any potential errors
        return jsonify({"message": "Error: " + str(e)})


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


@app.route("/aboutus")
def AboutUs():
    return render_template("aboutus.html")


@app.route("/cart")
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
            "cart.html",
            products=user_cart,
            cart_count=cart_count,
            total_price=total_price,
        )
    else:
        # User is not logged in
        return render_template("cart.html", products=[], cart_count=0, total_price=0)


@app.route("/storeprofile")
def Profile():
    return render_template("store_profile.html")


@app.route("/sellerdashboard")
def Dashboard():
    return render_template("seller_dashboard.html")


@app.route("/postingmerchandise")
def AddMerchandise():
    return render_template("posting_merchandise.html")


@app.route("/viewtransactions")
def Transactions():
    return render_template("view_transactions.html")


@app.route("/inventory")
def Inventory():
    return render_template("inventory.html")


@app.route("/accounting")
def Accounting():
    return render_template("accounting.html")


@app.route("/courier")
def Courier():
    return render_template("courier.html")


if __name__ == "__main__":
    app.run(debug=True)
