# Imports
from flask import Flask, redirect, render_template, request, url_for, flash, session
from sqlalchemy import create_engine, text

# IMPORT MODELS
import database as db

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

def get_user_role(conn, user_id):
    if conn.execute(text("SELECT 1 FROM admins WHERE admin_id = :id"), {"id": user_id}).first():
        return "admin"
    if conn.execute(text("SELECT 1 FROM vendors WHERE vendor_id = :id"), {"id": user_id}).first():
        return "vendor"
    if conn.execute(text("SELECT 1 FROM customers WHERE customer_id = :id"), {"id": user_id}).first():
        return "customer"
    return None


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
    if "user_id" not in session or not session.get("is_admin"):
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
    if not session.get("is_admin"):
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
    if not session.get("is_admin"):
        flash("Access denied.", "error")
        return redirect(url_for('index'))

    db.delete_product(conn, product_id)

    flash("Product deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/product/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    if not session.get("is_admin"):
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
    if not session.get("is_admin"):
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
    if not session.get("is_admin"):
        flash("Access denied.", "error")
        return redirect(url_for('index'))

    # Update status to 'Rejected'
    query = text("UPDATE returns SET status = 'Rejected' WHERE return_id = :id")
    conn.execute(query, {"id": return_id})
    conn.commit()

    flash(f"Return #{return_id} has been rejected.", "error")
    return redirect(url_for('admin_dashboard'))
  


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
        return "Unauthorized", 403

    customer_id = session["user_id"]

    items = db.get_cart_items(conn, customer_id)

    return render_template("cart.html", items=items)


# ===========
# ADD TO CART
# ===========

@app.route("/add-to-cart", methods=["POST"])
def add_cart():
    if session.get("role") != "customer":
        return "Unauthorized", 403

    customer_id = session["user_id"]
    variant_id = int(request.form.get("variant_id"))
    quantity = int(request.form.get("quantity", 1))

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
    db.add_to_cart(conn, cart["cart_id"], variant_id, quantity)

    flash("Added to cart!", "success")
    return redirect(url_for("shop"))


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


# =======
# RUN APP
# =======

if __name__ == "__main__":
    app.run(debug=True)