from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app_utils import get_user_role
from extensions import engine, rollback_app_connection
import database as db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
def admin_dashboard():
    with engine.connect() as conn:
        if "user_id" not in session or get_user_role(conn, session["user_id"]) != "admin":
            flash("Access denied.", "error")
            return redirect(url_for("index"))

        search_query = request.args.get("search")
        products = db.search_products(conn, search_query) if search_query else db.get_all_products(conn)
        returns = db.get_all_pending_returns(conn)
        orders = db.get_all_orders(conn)

    return render_template(
        "admin.html",
        products=products,
        returns=returns,
        orders=orders,
        search_query=search_query
    )


@admin_bp.route("/admin-returns")
def admin_returns():
    with engine.connect() as conn:
        if "user_id" not in session or get_user_role(conn, session["user_id"]) != "admin":
            return redirect(url_for("auth.login"))

        all_returns = db.get_all_pending_returns(conn)

    return render_template("admin-returns.html", returns=all_returns)


@admin_bp.route("/admin/returns/update/<int:return_id>", methods=["POST"])
def admin_update_return(return_id):
    new_status = request.form.get("status")
    with engine.connect() as conn:
        db.update_return_status(conn, return_id, new_status)
    return redirect(url_for("admin.admin_returns"))


@admin_bp.route("/danger", methods=["POST"])
def danger():
    rollback_app_connection()

    with engine.connect() as conn:
        if get_user_role(conn, session.get("user_id")) != "admin":
            flash("Access denied.", "error")
            return redirect(url_for("index"))

        rollback_app_connection()

        if db.reset_database(conn, "database/store_database_schema.sql", "database/seed_data.sql"):
            flash("Database reset successfully.", "success")
        else:
            flash("Failed to reset database.", "error")

    return redirect(url_for("index"))
