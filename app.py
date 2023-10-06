from flask import Flask, render_template

app = Flask(__name__)


@app.route("/homepage")
def BuyerHomePage():
    return render_template("buyer_homepage.html")


@app.route("/sellerprofile")
def SellerProfile():
    return render_template("seller_profile.html")


if __name__ == "__main__":
    app.run(debug=True)
