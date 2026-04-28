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
    total = 0 # Initialize total

    # Use a 'with' block to handle the connection safely
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

        # Calculate the total cost
        for item in cart_items:
            # Use discount_price if available, otherwise regular price
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
    
    with engine.connect() as conn:
        cart_items = db.get_cart_items(conn, customer_id)

        if not cart_items:
            flash("Cart is empty.", "error")
            return redirect(url_for("customer.cart")) # Added blueprint prefix

        total_price = 0
        for item in cart_items:
            price = item.get("discount_price") or item.get("price")
            total_price += float(price) * int(item["quantity"])

        order_id = db.create_order(conn, customer_id, total_price)

        for item in cart_items:
            db.add_order_item(conn, order_id, item["variant_id"], item["quantity"])

        conn.execute(text("""
            DELETE FROM cart_items 
            WHERE cart_id = (SELECT cart_id FROM carts WHERE customer_id = :cid)
        """), {"cid": customer_id})
        
        conn.commit()

    flash("Order placed successfully!", "success")
    # Make sure 'orders_page' is the correct function name in your blueprint
    return redirect(url_for("customer.orders_page"))