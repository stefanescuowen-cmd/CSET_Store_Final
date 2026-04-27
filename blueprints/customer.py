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