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

# ==================
# ADD ROLE DETECTION
# ==================

def get_user_role(connection, user_id):
    result = connection.execute(
        text("""
        SELECT 
            CASE
                WHEN EXISTS (SELECT 1 FROM admins WHERE admin_id = :id) THEN 'admin'
                WHEN EXISTS (SELECT 1 FROM vendors WHERE vendor_id = :id) THEN 'vendor'
                WHEN EXISTS (SELECT 1 FROM customers WHERE customer_id = :id) THEN 'customer'
                ELSE NULL
            END AS role
        """),
        {"id": user_id}
    ).mappings().first()

    return result["role"]


# ====
# HOME
# ====

@app.route("/")
def index():
    is_admin = session.get("role") == "admin"
    return render_template("index.html", is_admin=is_admin)


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

        success = db.register_new_user(conn, name, email, username, password, role)

        if not success:
            flash("Registration failed.", "error")
            return redirect(url_for("signup"))

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
            session["role"] = get_user_role(conn, user.user_id)
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
# ADMIN DASHBOARD
# =========
@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session or not get_user_role(conn, session["user_id"]) == "admin":
        flash("Access denied.", "error")
        return redirect(url_for('index'))
    
    # Get search query if it exists
    search_query = request.args.get("search")
    
    # 1. Fetch products
    if search_query:
        products = db.search_products(conn, search_query)
    else:
        products = db.get_all_products(conn)

    # 2. Fetch pending returns
    returns = db.get_all_pending_returns(conn)


    return render_template("admin.html", products=products, returns=returns, search_query=search_query)



# ========================
# ADMIN PRODUCT MANAGEMENT
# ========================
@app.route("/admin/product/new", methods=["GET", "POST"])
def new_product():
    if not get_user_role(conn, session["user_id"]) == "admin":
        flash("Access denied.", "error")
        return redirect(url_for('index'))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = float(request.form.get("price"))
        stock = int(request.form.get("stock"))

        db.add_new_product(conn, title, description, price, stock)

        flash("Product added successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template("new_product.html")

@app.route("/admin/product/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    if not get_user_role(conn, session["user_id"]) == "admin":
        flash("Access denied.", "error")
        return redirect(url_for('index'))

    db.delete_product(conn, product_id)

    flash("Product deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/product/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    if not get_user_role(conn, session["user_id"]) == "admin":
        flash("Access denied.", "error")
        return redirect(url_for('index'))

    title = request.form.get("title")
    description = request.form.get("description")
    price = float(request.form.get("price"))
    stock = int(request.form.get("stock"))
    discount_price = float(request.form.get("discount-price")) if request.form.get("discount-price") else None

    db.update_product(conn, product_id, title, description, price, discount_price, stock)

    flash(f"Product '{title}' successfully!", "success")
    return redirect(url_for('admin_dashboard'))


# ========================
# ADMIN RETURN MANAGEMENT
# ========================

@app.route("/admin/returns/<int:return_id>/approve", methods=["POST"])
def approve_return(return_id):
    if not get_user_role(conn, session["user_id"]) == "admin":
        flash("Access denied.", "error")
        return redirect(url_for('index'))

    # Update status to 'Confirmed'
    query = text("UPDATE returns SET status = 'Confirmed' WHERE return_id = :id")
    conn.execute(query, {"id": return_id})
    conn.commit()

    flash(f"Return #{return_id} has been confirmed.", "success")
    return redirect(url_for('admin_dashboard')) # Make sure this matches your admin route name


@app.route("/admin/returns/<int:return_id>/reject", methods=["POST"])
def reject_return(return_id):
    if not get_user_role(conn, session["user_id"]) == "admin":
        flash("Access denied.", "error")
        return redirect(url_for('index'))

    # Update status to 'Rejected'
    query = text("UPDATE returns SET status = 'Rejected' WHERE return_id = :id")
    conn.execute(query, {"id": return_id})
    conn.commit()

    flash(f"Return #{return_id} has been rejected.", "error")
    return redirect(url_for('admin_dashboard'))
  

# ==================
# CUSTOMER DASHBOARD
# ==================

@app.route("/customer")
def customer_dashboard():
    if session.get("role") != "customer" or not session.get("user_id"):
        return "Unauthorized", 403

    customer_id = session["user_id"]

    cart_items = db.get_cart_items(conn, customer_id)
    orders = db.get_orders(conn, customer_id)
    wishlist = db.get_wishlist(conn, customer_id)

    return render_template(
        "customer.html",
        cart_items=cart_items,
        orders=orders,
        wishlist=wishlist
    )


# ================
# VENDOR DASHBOARD
# ================

@app.route("/vendor")
def vendor_dashboard():
    if session.get("role") != "vendor":
        return "Unauthorized", 403

    vendor_id = session["user_id"]

    products = db.get_vendor_products(conn, vendor_id)
    orders = db.get_vendor_orders(conn, vendor_id)

    return render_template("vendor.html", products=products, orders=orders)

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
    if session.get("role") != "customer":
        flash("Please log in as a customer to view your cart.", "error")
        return redirect(url_for("login"))

    customer_id = session["user_id"]

    items = db.get_cart_items(conn, customer_id)

    grand_total = 0
    for item in items:
        price = item['discount_price'] if item['discount_price'] is not None else item['price']
        grand_total += price * item['quantity']

    return render_template("cart.html", items=items, grand_total=grand_total)


# ===========
# ADD TO CART
# ===========

@app.route("/add-to-cart", methods=["POST"])
def add_cart():
    if session.get("role") != "customer":
        flash("Unauthorized", "error")
        return redirect(url_for("login"))

    customer_id = session["user_id"]
    variant_id = int(request.form.get("variant_id"))
    requested_qty = int(request.form.get("quantity", 1))

    #Check stock
    available_stock = db.get_variant_stock(conn, variant_id)

    # Check how many are already in the cart
    existing_item = conn.execute(
        text("SELECT quantity FROM cart_items ci JOIN carts c ON ci.cart_id = c.cart_id WHERE c.customer_id = :cid AND ci.variant_id = :vid"),
        {"cid": customer_id, "vid": variant_id}
    ).fetchone()
    
    current_in_cart = existing_item[0] if existing_item else 0

    if current_in_cart + requested_qty > available_stock:
        flash(f"Cannot add more. Only {available_stock} available in total (you have {current_in_cart} in cart).", "error")
        return redirect(url_for("shop"))

    # 1. Get cart
    cart = conn.execute(
        text("SELECT cart_id FROM carts WHERE customer_id = :cid"),
        {"cid": customer_id}
    ).mappings().first()

    # 2. Create cart if missing
    if not cart:
        conn.execute(
            text("INSERT INTO carts (customer_id) VALUES (:cid)"),
            {"cid": customer_id}
        )
        conn.commit()

        cart = conn.execute(
            text("SELECT cart_id FROM carts WHERE customer_id = :cid"),
            {"cid": customer_id}
        ).mappings().first()

    # 3. Add item
    db.add_to_cart(conn, cart["cart_id"], variant_id, requested_qty)

    flash("Added to cart!", "success")
    return redirect(url_for("shop"))



# ============================
# UPDATE CART QUANTITY
# ============================
@app.route("/update-cart-quantity", methods=["POST"])
def update_cart_quantity():
    if session.get("role") != "customer":
        flash("Unauthorized", "error")
        return redirect(url_for("login"))

    variant_id = request.form.get("variant_id")
    new_quantity = int(request.form.get("quantity"))

    customer_id = session["user_id"]

    # get cart_id
    cart = conn.execute(
        text("SELECT cart_id FROM carts WHERE customer_id = :cid"),
        {"cid": customer_id}
    ).mappings().first()

    if cart:
        db.update_cart_quantity(conn, cart["cart_id"], variant_id, new_quantity)


    available_stock = db.get_variant_stock(conn, variant_id)
    if new_quantity > available_stock:
        flash(f"Only {available_stock} items available in stock.", "error")
    else:
        flash("Cart updated successfully!", "success")
    
    return redirect(url_for("cart"))



# ================
# REMOVE FROM CART
# ================

@app.route("/remove-from-cart", methods=["POST"])
def remove_from_cart_route():
    if "user_id" not in session:
        return redirect(url_for("login"))

    variant_id = request.form.get("variant_id")
    customer_id = session["user_id"]

    # get cart_id
    cart = conn.execute(
        text("SELECT cart_id FROM carts WHERE customer_id = :cid"),
        {"cid": customer_id}
    ).mappings().first()

    if cart:
        db.remove_from_cart(conn, cart["cart_id"], variant_id)

    flash("Item removed from cart.", "success")
    return redirect(url_for("cart"))

# ===============
# ADD TO WISHLIST
# ===============

@app.route("/add-to-wishlist", methods=["POST"])
def add_wishlist():
    if session.get("role") != "customer":
        return "Unauthorized", 403

    variant_id = request.form.get("variant_id")

    db.add_to_wishlist(conn, session["user_id"], variant_id)

    flash("Added to wishlist!", "success")
    return redirect(url_for("shop"))

# =============
# VIEW WISHLIST
# =============

@app.route("/wishlist")
def wishlist():
    if "user_id" not in session:
        return redirect(url_for("login"))

    items = db.get_wishlist(conn, session["user_id"])
    return render_template("wishlist.html", items=items)


# ==============
# CHECKOUT ROUTE
# ==============

@app.route("/checkout", methods=["GET"])
def checkout():
    if session.get("role") != "customer":
        return "Unauthorized", 403

    customer_id = session["user_id"]

    # get cart items (reuses your existing function)
    cart_items = db.get_cart_items(conn, customer_id)

    if not cart_items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart"))

    total = 0

    # calculate total safely
    for item in cart_items:
        price = item.get("discount_price") or item.get("price")
        total += price * item["quantity"]

    return render_template(
        "checkout.html",
        items=cart_items,
        total=total,
    )


# ===========
# PLACE ORDER
# ===========

@app.route("/place-order", methods=["POST"])
def place_order():
    if session.get("role") != "customer":
        return "Unauthorized", 403

    customer_id = session["user_id"]

    cart_items = db.get_cart_items(conn, customer_id)

    if not cart_items:
        flash("Cart is empty.", "error")
        return redirect(url_for("cart"))

    # 1. Create order (USE YOUR FUNCTION)
    order_id = db.create_order(conn, customer_id)

    # 2. Add items (USE YOUR FUNCTION)
    for item in cart_items:
        db.add_order_item(
            conn,
            order_id,
            item["variant_id"],
            item["quantity"]
        )

    # 3. Clear cart
    cart_id = conn.execute(text("""
        SELECT cart_id FROM carts WHERE customer_id = :cid
    """), {"cid": customer_id}).scalar()

    conn.execute(text("""
        DELETE FROM cart_items WHERE cart_id = :cid
    """), {"cid": cart_id})

    conn.commit()

    flash("Order placed successfully!", "success")
    return redirect(url_for("customer_dashboard"))


# ============================
# ADD PRODUCT
# ============================
@app.route("/add-product", methods=["POST", "GET"])
def add_product():
    if not get_user_role(conn, session["user_id"]) == "admin" and not get_user_role(conn, session["user_id"]) == "vendor":
        flash("Must be a vendor or admin to access.", "error")
        return redirect(url_for('index'))
    
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = float(request.form.get("price"))
        discount_price = request.form.get("discount_price") if request.form.get("discount_price") else None
        discount_end = request.form.get("discount_end") if request.form.get("discount_end") else None

        colors = request.form.getlist("variant_color[]")
        sizes = request.form.getlist("variant_size[]")
        stocks = request.form.getlist("variant_stock[]")

        variants = []
        for i in range(len(colors)):
            variants.append({
                "color": colors[i],
                "size": sizes[i],
                "stock": int(stocks[i])
            })

        db.add_new_product(conn, session["user_id"], title, description, price, discount_price, discount_end, variants)

        print(variants)

        flash("Product added successfully!", "success")
        return redirect(url_for('vendor_dashboard'))
    
    return render_template("add-product.html")
  
  
# =============
# ACCOUNT ROUTE
# =============

@app.route("/account")
def account():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    role = session.get("role")

    user = conn.execute(
        text("SELECT user_id, name, email, username FROM users WHERE user_id = :id"),
        {"id": user_id}
).mappings().first()

    return render_template(
        "account.html",
        user=user,
        role=role
    )


# ========
# RESET DB
# ========

@app.route("/danger", methods=["POST"])
def danger():
    if not get_user_role(conn, session["user_id"]) == "admin":
        flash("Access denied.", "error")
        return redirect(url_for('index'))

    if  db.reset_database(conn, "database/store_database_schema.sql", "database/seed_data.sql"):
        flash("Database reset successfully.", "success")
    else:
        flash("Failed to reset database.", "error")

    return redirect(url_for('index'))


# =======
# RUN APP
# =======

if __name__ == "__main__":
    app.run(debug=True)