from datetime import datetime

from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from sqlalchemy import text
from extensions import engine
import database as db

customer_bp = Blueprint('customer', __name__)

@customer_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not session.get("user_id"):
        flash("Please log in to checkout.", "error")
        return redirect(url_for("auth.login"))

    customer_id = session["user_id"]
    sub_total = 0
    tax = 0
    grand_total = 0

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
            price = item['discount_price'] if item['discount_price'] is not None and (not item['discount_deadline'] or item['discount_deadline'] > datetime.now()) else item['price']
            sub_total += float(price) * int(item["quantity"])

        tax = sub_total * 0.08  # Assuming 8% tax rate
        grand_total = sub_total + tax

        
        sub_total = f"{sub_total:.2f}"
        tax = f"{tax:.2f}"
        
        grand_total = f"{grand_total:.2f}"

        return render_template(
            "checkout.html",
            items=cart_items,
            sub_total=sub_total,
            tax=tax,
            grand_total=grand_total,
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
            return redirect(url_for("cart"))

        for item in cart_items:
            if int(item["quantity"]) > int(item["stock"]):
                flash(f"{item['title']} only has {item['stock']} left in stock. Please update your cart.", "error")
                return redirect(url_for("cart"))

        total_price = 0
        for item in cart_items:
            price = item['discount_price'] if item['discount_price'] is not None and (not item['discount_deadline'] or item['discount_deadline'] > datetime.now()) else item['price']

            total_price += float(price) * int(item["quantity"])

        total_price = round(total_price * 1.08, 2)

        try:
            result = conn.execute(text("""
                INSERT INTO orders (customer_id, order_status, total_price)
                VALUES (:customer_id, 'Pending', :total_price)
            """), {"customer_id": customer_id, "total_price": total_price})
            order_id = result.lastrowid or conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

            for item in cart_items:
                stock_update = conn.execute(text("""
                    UPDATE product_variants
                    SET stock = stock - :quantity
                    WHERE variant_id = :variant_id AND stock >= :quantity
                """), {
                    "variant_id": item["variant_id"],
                    "quantity": item["quantity"]
                })

                if stock_update.rowcount != 1:
                    raise ValueError(f"Not enough stock for {item['title']}.")

                conn.execute(text("""
                    INSERT INTO order_items (order_id, variant_id, quantity, item_status)
                    VALUES (:order_id, :variant_id, :quantity, 'Pending')
                """), {
                    "order_id": order_id,
                    "variant_id": item["variant_id"],
                    "quantity": item["quantity"]
                })

            conn.execute(text("""
                DELETE FROM cart_items
                WHERE cart_id = (SELECT cart_id FROM carts WHERE customer_id = :cid)
            """), {"cid": customer_id})
            conn.commit()
        except Exception as exc:
            conn.rollback()
            flash(str(exc), "error")
            return redirect(url_for("cart"))

    flash("Order placed successfully!", "success")
    return redirect(url_for("orders_page"))


@customer_bp.route("/manage-addresses", methods=["GET", "POST"])
def manage_addresses():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    
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
        return redirect(url_for("auth.login"))
    
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
    

@customer_bp.route("/delete-address/<int:id>", methods=["POST"])
def delete_address(id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
        
    customer_id = session["user_id"]
    
    with engine.connect() as conn:
        # Delete only if the address belongs to the logged-in user
        conn.execute(text("DELETE FROM addresses WHERE address_id = :aid AND user_id = :uid"), 
                     {"aid": id, "uid": customer_id})
        conn.commit()
        
    flash("Address deleted successfully.", "success")
    return redirect(url_for("customer.manage_addresses"))
@customer_bp.route("/set-default-address/<int:id>", methods=["POST"])
def set_default_address(id):
    customer_id = session["user_id"]
    with engine.connect() as conn:
        # Reset all to 0
        conn.execute(text("UPDATE addresses SET is_default = 0 WHERE user_id = :uid"), {"uid": customer_id})
        # Set selected to 1
        conn.execute(text("UPDATE addresses SET is_default = 1 WHERE address_id = :aid AND user_id = :uid"), 
                     {"aid": id, "uid": customer_id})
        conn.commit()
    return redirect(url_for("customer.manage_addresses"))
