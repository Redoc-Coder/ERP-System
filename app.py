from flask import Flask, render_template

app = Flask(__name__)


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
