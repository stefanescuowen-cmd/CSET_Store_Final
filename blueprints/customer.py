from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from sqlalchemy import text
from extensions import engine
import database as db

customer_bp = Blueprint('customer', __name__)

@customer_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not session.get("user_id"):
        flash("Please log in to checkout.", "error")
        return redirect(url_for("login"))

    customer_id = session["user_id"]
    total = 0

    with engine.connect() as conn:
        addresses = db.get_user_addresses(conn, customer_id)
        if not addresses:
            flash("Please add a shipping address before checking out.", "info")
            # Ensure your address management route is also in this blueprint
            return redirect(url_for("customer.manage_addresses")) 

        cart_items = db.get_cart_items(conn, customer_id)
        
        if not cart_items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for("cart"))

        for item in cart_items:
            price = item.get("discount_price") or item.get("price")
            total += float(price) * int(item["quantity"])

        return render_template(
            "checkout.html",
            items=cart_items,
            total=total,
            addresses=addresses
        )
    

@customer_bp.route("/place-order", methods=["POST"])
def place_order():
    if session.get("role") != "customer":
        return "Unauthorized", 403

    customer_id = session["user_id"]
    
    # --- DUMMY PAYMENT VALIDATION ---
    method = request.form.get("payment_method")
    if method == "card":
        card_num = request.form.get("card_number")
        if not card_num or len(card_num) < 16:
            flash("Invalid Card Number. Must be 16 digits.", "error")
            return redirect(url_for("customer.checkout"))
    elif method == "paypal":
        if not request.form.get("paypal_email"):
            flash("PayPal email is required.", "error")
            return redirect(url_for("customer.checkout"))
    # --------------------------------

    with engine.connect() as conn:
        cart_items = db.get_cart_items(conn, customer_id)
        if not cart_items:
            flash("Cart is empty.", "error")
            return redirect(url_for("customer.cart"))

        total_price = 0
        for item in cart_items:
            price = item.get("discount_price") or item.get("price")
            total_price += float(price) * int(item["quantity"])

        # Create order and clear cart...
        order_id = db.create_order(conn, customer_id, total_price)
        for item in cart_items:
            db.add_order_item(conn, order_id, item["variant_id"], item["quantity"])

        conn.execute(text("""
            DELETE FROM cart_items 
            WHERE cart_id = (SELECT cart_id FROM carts WHERE customer_id = :cid)
        """), {"cid": customer_id})
        conn.commit()

    flash("Order placed successfully!", "success")
    return redirect(url_for("customer.orders_page"))


@customer_bp.route("/manage-addresses", methods=["GET", "POST"])
def manage_addresses():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    customer_id = session["user_id"]
    
    with engine.connect() as conn:
        if request.method == "POST":
            # Collect form data
            addr_data = {
                'name': request.form.get("receiver_name"),
                'phone': request.form.get("contact_number"),
                'l1': request.form.get("address_line1"),
                'l2': request.form.get("address_line2"),
                'city': request.form.get("city"),
                'state': request.form.get("state"),
                'zip': request.form.get("zip_code"),
                'type': request.form.get("address_type"),
                'default': 'is_default' in request.form
            }
            db.add_address(conn, customer_id, addr_data)
            flash("Address added successfully!", "success")
            return redirect(url_for("customer.manage_addresses"))

        addresses = db.get_user_addresses(conn, customer_id)
        return render_template("manage_addresses.html", addresses=addresses)
    

@customer_bp.route("/edit-address/<int:id>", methods=["GET", "POST"])
def edit_address(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    customer_id = session["user_id"]
    
    with engine.connect() as conn:
        if request.method == "POST":
            is_default = 1 if 'is_default' in request.form else 0
            
            # THE RESET LOGIC
            if is_default == 1:
                conn.execute(text("UPDATE addresses SET is_default = 0 WHERE user_id = :uid"), 
                             {"uid": customer_id})

            # THE UPDATE LOGIC
            query = text("""
                UPDATE addresses SET 
                receiver_name = :name, contact_number = :phone, 
                address_line1 = :l1, address_line2 = :l2, 
                city = :city, state = :state, zip_code = :zip, 
                address_type = :type, is_default = :default
                WHERE address_id = :aid AND user_id = :uid
            """)
            conn.execute(query, {
                "name": request.form.get("receiver_name"),
                "phone": request.form.get("contact_number"),
                "l1": request.form.get("address_line1"),
                "l2": request.form.get("address_line2"),
                "city": request.form.get("city"),
                "state": request.form.get("state"),
                "zip": request.form.get("zip_code"),
                "type": request.form.get("address_type"),
                "default": is_default,
                "aid": id, "uid": customer_id
            })
            conn.commit()
            flash("Address updated!", "success")
            return redirect(url_for("customer.manage_addresses"))

        result = conn.execute(text("SELECT * FROM addresses WHERE address_id = :aid AND user_id = :uid"), 
                              {"aid": id, "uid": customer_id}).mappings().first()
        
        if not result:
            flash("Address not found.", "error")
            return redirect(url_for("customer.manage_addresses"))
            
        return render_template("edit_address.html", address=result)
    

@customer_bp.route("/orders")
def orders_page():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    
    customer_id = session["user_id"]
    with engine.connect() as conn:
        orders = db.get_user_orders(conn, customer_id)
        return render_template("orders.html", orders=orders)