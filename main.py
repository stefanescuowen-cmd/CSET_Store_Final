from datetime import datetime

from flask import Flask, make_response, redirect, render_template, request, url_for, flash, session
from app_utils import get_user_role
from extensions import app_conn, engine, rollback_app_connection
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

# IMPORT MODELS
import database as db

app = Flask(__name__)
app.secret_key = "school_project_key"

conn = app_conn


@app.after_request
def release_global_connection_locks(response):
    rollback_app_connection()
    return response


# ====
# HOME
# ====

@app.route("/")
def index():
    is_admin = session.get("role") == "admin"
    categories = db.get_unique_categories(conn)
    return render_template("index.html", is_admin=is_admin, categories=categories)


# ======
# ORDERS
# ======

@app.route("/orders")
def orders_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    role = session.get("role")

    vendor_id = None

    with engine.connect() as conn:
        if role == "admin":
            orders_raw = db.get_all_orders(conn)

        elif role == "vendor":
            vendor = db.get_vendor_by_id(conn, user_id)
            vendor_id = vendor["vendor_id"] if vendor else None
            orders_raw = db.get_vendor_orders(conn, vendor_id)

        else:
            orders_raw = db.get_orders(conn, user_id)

        seen_order_ids = set()
        orders = []

        for order in orders_raw:
            order_dict = dict(order)

            if order_dict['order_id'] in seen_order_ids:
                continue
            seen_order_ids.add(order_dict['order_id'])

            order_items = db.get_order_items(conn, order_dict['order_id'])

            if role == 'vendor':
                order_items = [
                    i for i in order_items
                    if int(i['vendor_id']) == int(vendor_id)
                ]

            order_dict['order_items_list'] = order_items
            orders.append(order_dict)

    return render_template("orders.html", orders=orders, vendor_id=vendor_id)
  

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

# =========
# SHOP PAGE
# =========

@app.route("/shop")
def shop():
    args = {
        "search": request.args.get("search", ""),
        "color": request.args.get("color", ""),
        "size": request.args.get("size", ""), # This is now captured
        "availability": request.args.get("availability", ""),
        "category": request.args.get("category", "")
    }

    products = db.get_filtered_products(conn, **args)
    
    now = datetime.now()
    for p in products:
        if p.get('discount_deadline'):
            deadline = p['discount_deadline']
            if deadline > now:
                delta = deadline - now
                p['days_left'] = delta.days
                p['hours_left'] = delta.seconds // 3600
                p['mins_left'] = (delta.seconds // 60) % 60
            else:
                p['discount_price'] = None
                
    images = db.get_product_images(conn)
    
    # NEW: Fetch dynamic lists for the dropdowns
    colors = db.get_unique_colors(conn)
    categories = db.get_unique_categories(conn)
    sizes = db.get_unique_sizes(conn) # ADD THIS LINE

    image_map = {}
    for img in images:
        image_map.setdefault(img["product_id"], []).append(img["image_url"])
        
    return render_template(
        "shop.html",
        products=products, 
        image_map=image_map, 
        args=args,
        colors=colors,
        categories=categories,
        sizes=sizes
    )


# ============
# PRODUCT PAGE
# ============

@app.route("/product/<int:product_id>")
def product(product_id):
    product = db.get_product_by_id(conn, product_id)
    reviews = db.get_reviews_for_product(conn, product_id)
    return render_template("product.html", product=product, reviews=reviews)


# ====
# CART
# ====

@app.route("/cart")
def cart():
    if session.get("role") != "customer":
        flash("Please log in as a customer to view your cart.", "error")
        return redirect(url_for("auth.login"))

    customer_id = session["user_id"]

    items = db.get_cart_items(conn, customer_id)

    grand_total = 0
    for item in items:
        price = item['discount_price'] if item['discount_price'] is not None and (not item['discount_deadline'] or item['discount_deadline'] > datetime.now()) else item['price']
        grand_total += price * item['quantity']

    grand_total = f"{grand_total:.2f}"


    response = make_response(render_template("cart.html", items=items, grand_total=grand_total, now=datetime.now()))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ===========
# ADD TO CART
# ===========

@app.route("/add-to-cart", methods=["POST"])
def add_cart():
    if session.get("role") != "customer":
        flash("Unauthorized", "error")
        return redirect(url_for("auth.login"))

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



# ====================
# UPDATE CART QUANTITY
# ====================

@app.route("/update-cart-quantity", methods=["POST"])
def update_cart_quantity():
    if session.get("role") != "customer":
        flash("Unauthorized", "error")
        return redirect(url_for("auth.login"))

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
        return redirect(url_for("auth.login"))

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
        return redirect(url_for("auth.login"))

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
        return redirect(url_for("auth.login"))

    items = db.get_wishlist(conn, session["user_id"])
    return render_template("wishlist.html", items=items)

# =============
# ACCOUNT ROUTE
# =============

@app.route("/account")
def account():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

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

@app.route("/update-password", methods=["POST"])
def update_password():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to update your password.", "error")
        return redirect(url_for("auth.login"))
    
    current_pw = request.form.get("current_password")
    new_pw = request.form.get("new_password")

    user = db.get_user_by_id(conn, user_id)

    stored_pw = user['password'] or ''
    current_ok = (check_password_hash(stored_pw, current_pw) if (stored_pw.startswith('pbkdf2:') or stored_pw.startswith('scrypt:')) else stored_pw == current_pw)

    if not current_ok:
        flash("Current password is incorrect.", "error")
        return redirect(url_for("account"))
    
    if not new_pw or len(new_pw) < 4:
        flash("New password must be at least 4 characters long.", "error")
        return redirect(url_for("account"))
    
    if new_pw == current_pw:
        flash("New password cannot be the same as the current password.", "error")
        return redirect(url_for("account"))
    
    db.update_user_password(conn, user_id, generate_password_hash(new_pw))

    flash("Password updated successfully!", "success")
    return redirect(url_for("account"))

@app.route("/update-user-details", methods=["POST"])
def update_user_details():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to update your details.", "error")
        return redirect(url_for("auth.login"))

    name = request.form.get("name")
    email = request.form.get("email")
    username = request.form.get("username")

    db.update_user_details(conn, user_id, name, email, username)

    flash("Details updated successfully!", "success")
    return redirect(url_for("account"))


# =====================
# CUSTOMER RETURN ROUTE
# =====================

@app.route("/submit-return", methods=["POST"])
def submit_return():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db.create_return_request(
        conn,
        customer_id=session["user_id"],
        order_id=request.form.get("order_id"),
        variant_id=request.form.get("variant_id"),
        title=request.form.get("title"),
        description=request.form.get("description"),
        demand=request.form.get("demand")
    )
    return redirect(url_for("my_returns"))

@app.route("/my-returns")
def my_returns():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    customer_id = session["user_id"]
    with engine.connect() as conn:
        user_returns = db.get_customer_returns(conn, customer_id)
        
        # Get orders and nest the items just like we did for the orders page
        raw_orders = db.get_orders(conn, customer_id)
        orders = []
        for r in raw_orders:
            o_dict = dict(r)
            # Fetch items for this specific order
            o_dict['order_items_list'] = db.get_order_items(conn, o_dict['order_id'])
            orders.append(o_dict)
            
    return render_template("my-returns.html", returns=user_returns, orders=orders)

# =======
# REVIEWS
# =======

@app.route("/reviews")
def reviews_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    sort_selection = request.args.get('sort', 'date')
    rating_filter = request.args.get('rating', type=int)
    p_id = request.args.get('product_id', type=int)

    with engine.connect() as connection:
        all_products = connection.execute(
            text("SELECT product_id, title FROM products ORDER BY title")
        ).mappings().all()

        # 1. Fetch reviews using your DB helper
        reviews = db.get_all_reviews(
            connection, 
            product_id=p_id, 
            sort_by=sort_selection, 
            filter_rating=rating_filter
        )
        
        # 2. Fetch product details (including category) for the header
        product = None
        if p_id:
            product = connection.execute(
                text("SELECT title, category FROM products WHERE product_id = :id"), 
                {"id": p_id}
            ).mappings().first()
       
        if not product:
            product = {"title": "All Products", "category": "General"}

    return render_template(
        "reviews.html",
        reviews=reviews,
        all_products=all_products,
        current_sort=sort_selection, 
        current_filter=rating_filter,
        product=product,
        product_id=p_id
    )


# ==========
# ADD REVIEW
# ==========

@app.route("/add-review", methods=["POST"])
def add_review_route():
    product_id = request.form.get("product_id")
    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment")

    if not product_id or not rating:
        flash("Invalid review data.", "error")
        return redirect(url_for("shop"))
    
    if db.review_exists(conn, product_id, session["user_id"]):
        flash("You have already reviewed this product.", "error")
        return redirect(url_for("reviews_page", product_id=product_id))

    with engine.connect() as connection:
        # Directly call add_review using product_id
        db.add_review(
            connection=connection, 
            product_id=product_id, # Updated parameter name
            customer_id=session["user_id"], 
            rating=rating, 
            description=comment
        )
        connection.commit()
        flash("Review submitted!", "success")
    
    return redirect(url_for("reviews_page", product_id=product_id))


# ============
# CHAT PAGE
# ============

@app.route('/chat')
def chat():
    user_id = session.get('user_id')
    role = session.get('role') 
    
    if not user_id:
        return redirect('/login')
    
    is_new = request.args.get('new_chat') == 'true'
    
    def to_int(val):
        return int(val) if val and val.isdigit() else None

    cid = to_int(request.args.get('cid'))
    vid = to_int(request.args.get('vid'))
    aid = to_int(request.args.get('aid'))
    rid = to_int(request.args.get('rid'))

    with engine.connect() as conn:
        vendor_id = user_id
        if role == 'vendor':
            vendor = db.get_vendor_by_id(conn, user_id)
            if not vendor:
                flash("Vendor profile not found.", "error")
                return redirect(url_for("index"))
            vendor_id = vendor["vendor_id"]

        sidebar_chats = db.get_chat_list(conn, vendor_id if role == 'vendor' else user_id, role)

        #for new chat stuff
        recipients = []
        admins = []
        returns = []
        if is_new:
            if role == 'customer':
                recipients = db.get_all_vendors(conn)
                admins = db.get_all_admins(conn)
                returns = db.get_customer_returns(conn, user_id)
            elif role == 'vendor':
                recipients = db.get_vendor_customers(conn, vendor_id)
            elif role == 'admin':
                recipients = db.get_all_customers(conn)

        


        #for existing chat stuff
        history = []

        
        cname = db.get_user_name(conn, cid) if cid else None
        vname = db.get_user_name(conn, vid) if vid else None
        aname = db.get_user_name(conn, aid) if aid else None
        rname = db.get_return_title(conn, rid) if rid else None

        if cid:
            history = db.get_specific_chat_history(conn, customer_id=cid, vendor_id=vid, admin_id=aid, return_id=rid)
        
        return render_template('chat.html', 
                                sidebar_chats=sidebar_chats, 
                                history=history,
                                is_new = is_new,
                                recipients=recipients,
                                admins=admins,
                                returns=returns,
                                curr_cid=cid,
                                curr_vid=vid,
                                curr_aid=aid,
                                curr_rid=rid,
                                current_vendor_id=vendor_id if role == 'vendor' else None,
                                cname=cname,
                                vname=vname,
                                aname=aname,
                                rname=rname)
    

#===========
#SEND MESSAGE
#===========
@app.route("/send_message", methods=["POST"])
def send_message():
    user_id = session.get('user_id')
    role = session.get('role')

    def clean_id(val):
        if val is None or str(val).strip().lower() in ['', 'none', 'null']:
            return None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    # 1. Capture basic info
    text_msg = request.form.get("message")
    reason = request.form.get("reason") # Only present in NEW chat form
    
    # 2. Determine IDs based on whether this is a NEW chat or a REPLY
    if reason:
        # --- New Chat Logic ---
        cid = clean_id(request.form.get("cid"))
        if reason == "question":
            vid = clean_id(request.form.get("vid_choice"))
            aid = None
            rid = None
        else: # reason == "return"
            vid = None
            aid = clean_id(request.form.get("aid_choice"))
            rid = clean_id(request.form.get("return_choice"))
    else:
        # --- Reply Logic ---
        cid = clean_id(request.form.get("cid"))
        vid = clean_id(request.form.get("vid"))
        aid = clean_id(request.form.get("aid"))
        rid = clean_id(request.form.get("rid"))

    # 3. Ensure Sender's ID is correctly assigned to their role column
    final_vid = vid
    final_aid = user_id if role == 'admin' else aid
    final_cid = user_id if role == 'customer' else cid

    # 4. Save to Database
    with engine.connect() as conn:
        if role == 'vendor':
            vendor = db.get_vendor_by_id(conn, user_id)
            if not vendor:
                flash("Vendor profile not found.", "error")
                return redirect(url_for("chat"))
            final_vid = vendor["vendor_id"]

        db.send_chat_message(
            conn,
            sender_id=user_id, 
            customer_id=final_cid, 
            text_content=text_msg, 
            vendor_id=final_vid, 
            admin_id=final_aid, 
            return_id=rid
        )

    return redirect(url_for("chat", cid=final_cid, vid=final_vid, aid=final_aid, rid=rid))

# ===================
# REGISTER BLUEPRINTS
# ===================
from blueprints.customer import customer_bp
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.vendor import vendor_bp

app.register_blueprint(customer_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(vendor_bp)

# =======
# RUN APP
# =======

if __name__ == "__main__":
    app.run(debug=True)
