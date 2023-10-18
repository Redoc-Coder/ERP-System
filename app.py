import os
from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, accounts
from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'my_key'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/")
def LandingPage():
    return render_template("landingpage.html")


@app.route("/login", methods=['GET','POST'])
def Login():
     error = None
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the database for a user with the given username
        user = accounts.query.filter_by(email=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('LandingPage'))  # Redirect to the dashboard or another page
         
        else:
            error = 'Invalid email or password. Please try again.'


     return render_template('login.html', error=error)


@app.route("/signup", methods=['GET','POST'])
def SignUp():
     error = None
     if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        account_type = request.form['accountType']  # Account Type field should match the form field name
        password = request.form['password']

        if accounts.query.filter_by(email=email).first():
            error = 'Email already exists. Please choose another email.'
        else:
            
        # Create a new Account object and insert it into the database
            new_account = accounts(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                account_type=account_type,
                password=password

        )
            db.session.add(new_account)
            db.session.commit()

        


     return render_template('signup.html', error = error)

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
    return render_template("cart.html")


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