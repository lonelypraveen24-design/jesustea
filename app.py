from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


def get_db():
    return sqlite3.connect("orders.db")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/order")
def order():
    return render_template("order.html")


# ORDER SUBMIT (single order)
@app.route("/order-submit", methods=["POST"])
def order_submit():
    tea_name = request.form.get("tea")
    qty = int(request.form.get("qty", 1))

    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (tea_name, quantity) VALUES (?, ?)",
        (tea_name, qty),
    )
    conn.commit()
    conn.close()

    return render_template("success.html", tea=tea_name, qty=qty)


# ADD TO CART
@app.route("/add-to-cart/<tea>/<int:price>")
def add_to_cart(tea, price):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append({"tea": tea, "price": price})
    session.modified = True
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    total = sum(item["price"] for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total=total)


@app.route("/clear-cart")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("cart"))


@app.route("/checkout")
def checkout():
    cart_items = session.get("cart", [])
    total = sum(item["price"] for item in cart_items)
    return render_template("checkout.html", cart_items=cart_items, total=total)


# ✅ PLACE ORDER (FINAL FIX)
@app.route("/place-order", methods=["POST"])
def place_order():
    cart_items = session.get("cart", [])

    if not cart_items:
        return redirect(url_for("menu"))

    conn = get_db()
    c = conn.cursor()

    for item in cart_items:
        c.execute(
            "INSERT INTO orders (tea_name, quantity) VALUES (?, ?)",
            (item["tea"], 1),
        )

    conn.commit()
    conn.close()

    qty = len(cart_items)
    session.pop("cart", None)

    return render_template("success.html", tea="Your Order", qty=qty)


# ABOUT
@app.route("/about")
def about():
    return render_template("about.html")


# CONTACT
@app.route("/contact")
def contact():
    return render_template("contact.html")


# ADMIN LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "1234":
            session["admin"] = True
            return redirect(url_for("orders"))
        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


# VIEW ORDERS
@app.route("/orders")
def orders():
    if not session.get("admin"):
        return redirect(url_for("login"))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM orders")
    data = c.fetchall()
    conn.close()

    return render_template("orders.html", orders=data)


@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM orders")
    total_orders = c.fetchone()[0]

    c.execute("SELECT SUM(quantity) FROM orders")
    total_qty = c.fetchone()[0] or 0

    conn.close()

    return render_template(
        "dashboard.html",
        total_orders=total_orders,
        total_qty=total_qty,
    )


if __name__ == "__main__":
    app.run(debug=True)



