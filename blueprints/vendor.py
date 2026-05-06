from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import text

from app_utils import get_user_role
from extensions import engine
import database as db

vendor_bp = Blueprint("vendor", __name__)


def _current_vendor(connection):
    user_id = session.get("user_id")
    if not user_id or get_user_role(connection, user_id) != "vendor":
        return None
    return db.get_vendor_by_id(connection, user_id)


@vendor_bp.route("/vendor")
def vendor_dashboard():
    if "user_id" not in session:
        flash("You need to log in as a vendor!", "error")
        return redirect(url_for("auth.login"))

    with engine.connect() as conn:
        vendor = _current_vendor(conn)
        if not vendor:
            flash("Only vendors can access this page!", "error")
            return redirect(url_for("index"))

        vendor_id = vendor["vendor_id"]
        products = db.get_vendor_products(conn, vendor_id)
        orders_raw = db.get_vendor_orders(conn, vendor_id)

        orders = []
        for order in orders_raw:
            order_dict = dict(order)
            order_dict["items"] = [
                item for item in db.get_order_items(conn, order_dict["order_id"])
                if int(item["vendor_id"]) == int(vendor_id)
            ]
            orders.append(order_dict)

    return render_template("vendor.html", products=products, orders=orders)


@vendor_bp.route("/admin/manage-products/")
def manage_products():
    user_id = session.get("user_id")

    with engine.connect() as conn:
        role = get_user_role(conn, user_id)
        if role not in ["admin", "vendor"]:
            flash("Access denied.", "error")
            return redirect(url_for("index"))

        if role == "admin":
            products = db.get_all_products(conn)
        else:
            vendor = db.get_vendor_by_id(conn, user_id)
            vendor_id = vendor["vendor_id"]
            products = db.get_products_by_vendor(conn, vendor_id)

    return render_template("manage-products.html", products=products, role=role)


@vendor_bp.route("/new-product/", methods=["GET", "POST"])
def new_product():
    user_id = session.get("user_id")

    with engine.connect() as conn:
        role = get_user_role(conn, user_id)
        if role not in ["admin", "vendor"]:
            flash("Access denied.", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            title = request.form.get("title")
            category = request.form.get("category")
            warranty = int(request.form.get("warranty") or 12)
            description = request.form.get("description")
            price = float(request.form.get("price") or 0)
            discount_price = request.form.get("discount_price") or None
            discount_end = request.form.get("discount_end") or None

            selected_vendor = request.form.get("vendor_id")
            if role == "admin":
                vendor_id = int(selected_vendor)
            else:
                vendor = db.get_vendor_by_id(conn, user_id)
                vendor_id = vendor["vendor_id"]

            images = request.form.getlist("image")
            variant_colors = request.form.getlist("variant_color[]")
            variant_sizes = request.form.getlist("variant_size[]")
            variant_stocks = request.form.getlist("variant_stock[]")

            variants = []
            for i in range(len(variant_colors)):
                variants.append({
                    "color": variant_colors[i],
                    "size": variant_sizes[i],
                    "stock": int(variant_stocks[i])
                })

            db.add_new_product(
                conn,
                vendor_id,
                title,
                description,
                price,
                discount_price,
                discount_end,
                variants,
                images,
                category,
                warranty
            )

            flash("Product added successfully!", "success")
            return redirect(url_for("vendor.manage_products"))

        vendors = db.get_all_vendors(conn) if role == "admin" else []

    return render_template("new-product.html", vendors=vendors, role=role, is_edit=False)


@vendor_bp.route("/add-product", methods=["GET", "POST"])
def add_product():
    user_id = session.get("user_id")

    with engine.connect() as conn:
        role = get_user_role(conn, user_id)
        if role not in ["admin", "vendor"]:
            flash("Must be a vendor or admin to access.", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            if role == "admin":
                vendor_id = request.form.get("vendor-id")
            else:
                vendor = db.get_vendor_by_id(conn, user_id)
                if not vendor:
                    flash("Vendor profile not found.", "error")
                    return redirect(url_for("index"))
                vendor_id = vendor["vendor_id"]

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

            images = request.form.getlist("image")
            db.add_new_product(
                conn,
                vendor_id,
                request.form.get("title"),
                request.form.get("description"),
                float(request.form.get("price")),
                request.form.get("discount_price") or None,
                request.form.get("discount_end") or None,
                variants,
                images,
                request.form.get("category"),
                int(request.form.get("warranty"))
            )

            flash("Product added successfully!", "success")
            if role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            return redirect(url_for("vendor.vendor_dashboard"))

    return render_template("add-product.html", role=role)


@vendor_bp.route("/admin/product/<int:product_id>/edit/", methods=["GET", "POST"])
def edit_product(product_id):
    user_id = session.get("user_id")

    with engine.connect() as conn:
        role = get_user_role(conn, user_id)
        product = db.get_product_by_id(conn, product_id)
        if not product:
            flash("Product not found.", "error")
            return redirect(url_for("vendor.manage_products"))

        if role == "vendor":
            vendor = db.get_vendor_by_id(conn, user_id)
            vendor_id = vendor["vendor_id"] if vendor else None
        else:
            vendor_id = None

        if role != "admin" and product.get("vendor_id") != vendor_id:
            flash("Access denied.", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            title = request.form.get("title")
            description = request.form.get("description")
            price = float(request.form.get("price") or 0)
            discount_price = request.form.get("discount_price") or None
            discount_end = request.form.get("discount_end") or None
            category = request.form.get("category")
            warranty = request.form.get("warranty")

            selected_vendor = request.form.get("vendor_id")
            if role == "admin":
                if not selected_vendor:
                    flash("Please select a vendor.", "error")
                    return redirect(request.url)
                vendor_id = int(selected_vendor)
            else:
                vendor_id = product.get("vendor_id")

            if discount_price is not None and float(discount_price) >= price:
                flash("Discount price must be less than the original price.", "error")
                return redirect(url_for("vendor.edit_product", product_id=product_id))

            db.update_product(
                conn, product_id, vendor_id, title, description, price,
                discount_price, discount_end, category, warranty
            )

            variant_ids = request.form.getlist("variant_id[]")
            colors = request.form.getlist("variant_color[]")
            sizes = request.form.getlist("variant_size[]")
            stocks = request.form.getlist("variant_stock[]")
            db.update_variants(conn, product_id, variant_ids, colors, sizes, stocks)

            images = request.form.getlist("image")
            final_images = [url for url in images if url.strip()]
            db.update_product_images(conn, product_id, final_images)

            flash(f"Product '{title}' updated successfully!", "success")
            return redirect(url_for("vendor.manage_products"))

        images = db.get_product_images_by_id(conn, product_id)
        variants = db.get_product_variants(conn, product_id)
        vendors = db.get_all_vendors(conn) if role == "admin" else []

    return render_template(
        "new-product.html",
        product=product,
        variants=variants,
        images=images,
        is_edit=True,
        role=role,
        vendors=vendors
    )


@vendor_bp.route("/admin/product/<int:product_id>/delete/", methods=["POST"])
def delete_product(product_id):
    user_id = session.get("user_id")

    with engine.connect() as conn:
        role = get_user_role(conn, user_id)
        product = db.get_product_by_id(conn, product_id)
        vendor = db.get_vendor_by_id(conn, user_id) if role == "vendor" else None
        vendor_id = vendor["vendor_id"] if vendor else None

        if role == "admin" or (product and product.get("vendor_id") == vendor_id):
            db.delete_product(conn, product_id)
            flash("Product deleted successfully!", "success")
        else:
            flash("Unauthorized action.", "error")

    return redirect(url_for("vendor.manage_products"))


@vendor_bp.route("/vendor/update_item_status", methods=["POST"])
def vendor_update_order_item_status():
    if session.get("role") != "vendor":
        return "Unauthorized", 403

    with engine.connect() as conn:
        vendor = db.get_vendor_by_id(conn, session.get("user_id"))
        if not vendor:
            flash("Vendor profile not found.", "danger")
            return redirect(url_for("orders_page"))

        vendor_id = vendor["vendor_id"]
        order_id = request.form.get("order_id")
        variant_id = request.form.get("variant_id")
        new_status = request.form.get("status")

        check_ownership = conn.execute(text("""
            SELECT p.vendor_id
            FROM products p
            JOIN product_variants v ON p.product_id = v.product_id
            WHERE v.variant_id = :v_id
        """), {"v_id": variant_id}).fetchone()

        if not check_ownership or int(check_ownership[0]) != int(vendor_id):
            flash("Error: You do not have permission to update this item.", "danger")
            return redirect(url_for("orders_page"))

        conn.execute(text("""
            UPDATE order_items
            SET item_status = :status
            WHERE order_id = :order_id AND variant_id = :variant_id
        """), {"status": new_status, "order_id": order_id, "variant_id": variant_id})
        conn.commit()

    flash_type = "success" if new_status != "Denied" else "warning"
    flash(f"Item status updated to {new_status}!", flash_type)
    return redirect(url_for("orders_page"))
