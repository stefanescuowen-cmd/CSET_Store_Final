# Imports
from flask import Flask, redirect, render_template, request, url_for, flash, session, jsonify
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



# ===============
# ADMIN DASHBOARD
# ===============

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

    orders = db.get_all_orders(conn)

    return render_template(
    "admin.html",
    products=products,
    returns=returns,
    orders=orders,
    search_query=search_query
)


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

# ======
# ORDERS
# ======

@app.route("/orders")
def orders_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    customer_id = session["user_id"]
    orders = db.get_orders(conn, customer_id)

    return render_template("orders.html", orders=orders)


# ===================
# ADMIN APPROVE ORDER
# ===================

@app.route("/admin/orders/<int:order_id>/approve", methods=["POST"])
def approve_order(order_id):
    if get_user_role(conn, session["user_id"]) != "admin":
        return "Unauthorized", 403

    conn.execute(text("""
        UPDATE orders
        SET order_status = 'Confirmed'
        WHERE order_id = :id
    """), {"id": order_id})

    conn.commit()
    return redirect(url_for("admin_dashboard"))


# ==================
# ADMIN REJECT ORDER
# ==================

@app.route("/admin/orders/<int:order_id>/reject", methods=["POST"])
def reject_order(order_id):
    if get_user_role(conn, session["user_id"]) != "admin":
        return "Unauthorized", 403

    conn.execute(text("""
        UPDATE orders
        SET order_status = 'Cancelled'
        WHERE order_id = :id
    """), {"id": order_id})

    conn.commit()
    return redirect(url_for("admin_dashboard"))
  

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
    if "user_id" not in session:
        flash('You need to log in as a vendor!', 'error')
        return redirect(url_for("login"))

    if get_user_role(conn, session["user_id"]) != "vendor":
        flash('Only vendors can access this page!', 'error')
        return redirect(url_for('index'))

    vendor_id = session["user_id"]

    products = db.get_vendor_products(conn, vendor_id)
    orders = db.get_vendor_orders(conn, vendor_id)

    return render_template(
        "vendor.html",
        products=products,
        orders=orders
    )


# ====================
# VENDOR APPROVE ORDER
# ====================

@app.route("/vendor/orders")
def vendor_orders():
    if session.get("role") != "vendor":
        return "Unauthorized", 403

    vendor_id = session["user_id"]
    orders = db.get_vendor_orders(conn, vendor_id)

    return render_template("vendor_orders.html", orders=orders)


# ====================
# VENDOR CONFIRM ORDER
# ====================

@app.route("/vendor/orders/confirm", methods=["POST"])
def vendor_confirm_order_item():
    if session.get("role") != "vendor":
        return "Unauthorized", 403

    order_id = request.form.get("order_id")
    variant_id = request.form.get("variant_id")
    vendor_id = session["user_id"]

    db.confirm_vendor_item(conn, order_id, vendor_id, variant_id)

    flash("Item confirmed for fulfillment", "success")
    return redirect(url_for("vendor_orders"))


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

    images = db.get_product_images(conn)

    image_map = {}
    for img in images:
        pid = img["product_id"]
        image_map.setdefault(pid, []).append(img["image_url"])

        
    return render_template("shop.html", products=products, search_term=search_term, image_map=image_map)


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
def add_to_wishlist():
    if session.get("role") != "customer":
        return "Unauthorized", 403

    variant_id = request.form.get("variant_id")
    customer_id = session["user_id"]

    db.add_to_wishlist(conn, customer_id, variant_id)

    flash("Added to wishlist!", "success")
    return redirect(url_for("shop"))

# ====================
# REMOVE FROM WISHLIST
# ====================

@app.route("/remove-from-wishlist", methods=["POST"])
def remove_from_wishlist():
    if not session.get("user_id"):
        flash("Please log in to add items to your cart.", "error")
        return redirect(url_for("login"))

    variant_id = request.form.get("variant_id")
    customer_id = session["user_id"]

    db.remove_from_wishlist(conn, customer_id, variant_id)

    flash("Removed from wishlist.", "success")
    return redirect(url_for("wishlist"))


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

@app.route("/checkout", methods=["POST", "GET"])
def checkout():
    if not session.get("user_id"):
        flash("Please log in to checkout.", "error")
        return redirect(url_for("login"))

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
    DELETE FROM cart_items WHERE cart_id = :cart_id
    """), {"cart_id": cart_id})

    conn.commit()

    flash("Order placed successfully!", "success")
    return redirect(url_for("customer_dashboard"))


# ===========
# ADD PRODUCT
# ===========

@app.route("/add-product", methods=["POST", "GET"])
def add_product():
    if not get_user_role(conn, session["user_id"]) == "admin" and not get_user_role(conn, session["user_id"]) == "vendor":
        flash("Must be a vendor or admin to access.", "error")
        return redirect(url_for('index'))
    
    role = session.get("role")
    
    if request.method == "POST":
        #send vendor id automatically if user is vendor and otherwise from the form
        if role == "admin":
            vendor_id = request.form.get("vendor-id")
        elif role == "vendor":
            vendor_id = session["user_id"]

        title = request.form.get("title")

        images = request.form.getlist("image")
        
        final_images = [url for url in images if url.strip()]

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

        db.add_new_product(conn, vendor_id, title, description, price, discount_price, discount_end, variants, final_images)

        flash("Product added successfully!", "success")
        if role == "admin":
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('vendor_dashboard'))
    
    return render_template("add-product.html", role=role)
  
  
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


# =======
# REVIEWS
# =======

@app.route("/reviews")
def reviews_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    reviews = db.get_all_reviews(conn)

    return render_template("reviews.html", reviews=reviews)

# ==========
# ADD REVIEW
# ==========

@app.route("/add-review", methods=["POST"])
def add_review_route():
    if "user_id" not in session:
        return redirect(url_for("login"))

    product_id = request.form.get("product_id")
    rating = request.form.get("rating")
    comment = request.form.get("comment")

    db.add_review(conn, session["user_id"], product_id, rating, comment)

    return redirect(url_for("shop"))


# =================
# CHAT HOME
# =================

@app.route("/chat")
def chat_home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    role = session.get("role")
    user_id = session["user_id"]

    conversations = []
    vendors = []
    admins = []

    if role == "customer":
        conversations = db.get_customer_conversations(conn, user_id)
        vendors = db.get_all_vendors(conn)
        admins = db.get_all_admins(conn)

    elif role == "vendor":
        conversations = db.get_vendor_conversations(conn, user_id)

        # Vendors should talk to admins OR customers depending on your design
        admins = db.get_all_admins(conn)

        # IMPORTANT: vendors should NOT see all vendors
        vendors = []

    elif role == "admin":
        conversations = db.get_admin_conversations(conn, user_id)

        # admins can talk to vendors + customers
        vendors = db.get_all_vendors(conn)

    else:
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    return render_template(
        "chat.html",
        conversations=conversations,
        messages=[],
        active_partner=None,
        vendors=vendors,
        admins=admins
    )


# =================
# CHAT WITH VENDOR
# =================

@app.route("/chat/vendor/<int:vendor_id>")
def chat_vendor(vendor_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    role = session.get("role")

    conversations = []

    if role == "customer":
        conversations = db.get_customer_conversations(conn, user_id)
        messages = db.get_customer_vendor_chat(conn, user_id, vendor_id)

    elif role == "vendor":
        conversations = db.get_vendor_conversations(conn, user_id)
        messages = db.get_vendor_chat(conn, user_id, vendor_id)

    elif role == "admin":
        conversations = db.get_admin_conversations(conn, user_id)
        messages = db.get_admin_chat(conn, user_id, vendor_id)

    vendors = db.get_all_vendors(conn)
    admins = db.get_all_admins(conn)

    return render_template(
        "chat.html",
        conversations=conversations,
        messages=messages,
        active_partner=("vendor", vendor_id),
        vendors=vendors,
        admins=admins
    )


# =================
# CHAT WITH ADMIN
# =================

@app.route("/chat/admin/<int:admin_id>")
def chat_admin(admin_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    role = session.get("role")

    conversations = []

    if role == "customer":
        conversations = db.get_customer_conversations(conn, user_id)
        messages = db.get_customer_admin_chat(conn, user_id, admin_id)

    elif role == "vendor":
        conversations = db.get_vendor_conversations(conn, user_id)
        messages = db.get_vendor_chat(conn, user_id, admin_id)

    elif role == "admin":
        conversations = db.get_admin_conversations(conn, user_id)
        messages = db.get_admin_chat(conn, user_id, admin_id)

    vendors = db.get_all_vendors(conn)
    admins = db.get_all_admins(conn)

    return render_template(
        "chat.html",
        conversations=conversations,
        messages=messages,
        active_partner=("admin", admin_id),
        vendors=vendors,
        admins=admins
    )


# =================
# CHAT API (REALTIME)
# =================

@app.route("/chat_messages/<partner_type>/<int:partner_id>")
def chat_messages(partner_type, partner_id):

    if "user_id" not in session:
        return jsonify([])

    user_id = session["user_id"]
    role = session.get("role")

    if role == "customer":
        if partner_type == "vendor":
            messages = db.get_customer_vendor_chat(conn, user_id, partner_id)
        else:
            messages = db.get_customer_admin_chat(conn, user_id, partner_id)

    elif role == "vendor":
        messages = db.get_vendor_chat(conn, user_id, partner_id)

    elif role == "admin":
        messages = db.get_admin_chat(conn, user_id, partner_id)

    else:
        messages = []

    return jsonify(messages)


# =================
# SEND MESSAGE
# =================

@app.route("/send_message", methods=["POST"])
def send_message():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    partner_type = request.form.get("partner_type")
    partner_id = int(request.form.get("partner_id"))
    text_msg = request.form.get("text")

    vendor_id = None
    admin_id = None

    if partner_type == "vendor":
        vendor_id = partner_id
    elif partner_type == "admin":
        admin_id = partner_id

    db.send_message(
        conn,
        user_id,
        vendor_id,
        admin_id,
        text_msg
    )

    return redirect(url_for("chat"))


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