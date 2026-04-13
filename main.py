# Imports
from flask import Flask, redirect, render_template, request, url_for, flash, session
from sqlalchemy import create_engine, text
from database import DatabaseManager

# IMPORT MODELS
from models.user import get_user_by_email_or_username, create_user, login_user
from models.products import get_all_products, get_product_by_id
from models.cart import get_cart_items, add_to_cart

import mysql.connector

app = Flask(__name__)
app.secret_key = "school_project_key"

# ===================
# DATABASE CONNECTION
# ===================

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="cset155",
    database="store_db"
)

# ====
# HOME
# ====

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# SIGNUP
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        role = request.form.get("role")
        name = request.form.get("name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        user = get_user_by_email_or_username(conn, email, username)

        if user:
            flash("User already exists.", "error")
            return redirect(url_for("signup"))

        create_user(conn, name, email, username, password)

        # Get user_id again
        user = get_user_by_email_or_username(conn, email, username)
        user_id = user["user_id"]

        cursor = conn.cursor()

        if role == "admin":
            cursor.execute("INSERT INTO admins VALUES (%s)", (user_id,))
        elif role == "vendor":
            cursor.execute("INSERT INTO vendors VALUES (%s)", (user_id,))
        else:
            cursor.execute("INSERT INTO customers VALUES (%s)", (user_id,))

        conn.commit()

        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

# =====
# LOGIN
# =====

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")
        password = request.form.get("password")

        user = login_user(conn, identifier, password)

        if not user:
            flash("Invalid login", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["user_id"]
        session["username"] = user["username"]

        flash("Logged in!", "success")
        return redirect(url_for("index"))

    return render_template("login.html")
  
  
# ========
# LOG OUT
# ========

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))
  


# =========
# SHOP PAGE
# =========

@app.route("/shop")
def shop():
    products = get_all_products(conn)
    return render_template("shop.html", products=products)


# ============
# PRODUCT PAGE
# ============

@app.route("/product/<int:product_id>")
def product(product_id):
    product = get_product_by_id(conn, product_id)
    return render_template("product.html", product=product)


# ====
# CART
# ====

@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    items = get_cart_items(conn, session["user_id"])
    return render_template("cart.html", items=items)


# ===========
# ADD TO CART
# ===========

@app.route("/add-to-cart", methods=["POST"])
def add_cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    variant_id = request.form.get("variant_id")
    quantity = int(request.form.get("quantity", 1))

    # Get or create cart FIRST
    cursor = conn.cursor()

    cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (session["user_id"],))
    cart = cursor.fetchone()

    if not cart:
        cursor.execute("INSERT INTO carts (customer_id) VALUES (%s)", (session["user_id"],))
        conn.commit()

        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (session["user_id"],))
        cart = cursor.fetchone()

    cart_id = cart[0]

    add_to_cart(conn, cart_id, variant_id, quantity)

    flash("Added to cart!", "success")
    return redirect(url_for("shop"))
  

  
# ========
# RESET DB
# ========

@app.route("/danger", methods=["POST"])
def danger():
    if not session.get("is_admin"):
        flash("Access denied.", "error")
        return redirect(url_for('index'))

    if db.reset_database("database/store_database_schema.sql", "database/seed_data.sql"):
        flash("Database reset successfully.", "success")
    else:
        flash("Failed to reset database.", "error")

    return redirect(url_for('index'))


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)