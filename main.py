# Imports
from flask import Flask, redirect, render_template, request, url_for, flash, session
from sqlalchemy import create_engine, text

# IMPORT MODELS
import database as db

import mysql.connector

app = Flask(__name__)
app.secret_key = "school_project_key"

# ===================
# DATABASE CONNECTION
# ===================

conn_str = "mysql://root:cset155@localhost/store_db"
engine = create_engine(conn_str, echo=True)

conn = engine.connect()

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

        user = db.verify_user(conn, email, password)

        if user:
            flash("User already exists.", "error")
            return redirect(url_for("signup"))

        db.register_new_user(conn, name, email, username, password)

        # Get user_id again
        user = db.verify_user(conn, email, password)
        user_id = user.user_id

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
        username_or_email = request.form.get("username_or_email")
        password = request.form.get("password")

        user = db.verify_user(conn, username_or_email, password)

        if user:
            session["user_id"] = user.user_id
            session["name"] = user.name
            session["username"] = user.username
            session["is_admin"] = db.is_admin(conn, user.user_id)
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials. Please try again.", "error")
            return redirect(url_for('login'))

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
    search_term = request.args.get("search")
    
    if search_term:
        # Use the search function from database.py
        products = db.search_products(conn, search_term)
    else:
        # Default view
        products = db.get_all_products(conn)
        
    return render_template("shop.html", products=products, search_term=search_term)


# ============
# PRODUCT PAGE
# ============

@app.route("/product/<int:product_id>")
def product(product_id):
    product = db.get_product_by_id(conn, product_id)
    return render_template("product.html", product=product)


# ====
# CART
# ====

@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    items = db.get_cart_items(conn, session["user_id"])
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

    db.add_to_cart(conn, cart_id, variant_id, quantity)

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

    if  db.reset_database(conn, "database/store_database_schema.sql", "database/seed_data.sql"):
        flash("Database reset successfully.", "success")
    else:
        flash("Failed to reset database.", "error")

    return redirect(url_for('index'))


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)