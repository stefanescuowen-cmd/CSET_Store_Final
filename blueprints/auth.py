from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app_utils import get_user_role
from extensions import engine
import database as db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        role = request.form.get("role")
        name = request.form.get("name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        with engine.connect() as conn:
            if db.user_exists(conn, email, username):
                flash("That email or username is already registered. Try logging in, or choose a different one.", "error")
                return redirect(url_for("auth.signup"))

            success = db.register_new_user(conn, name, email, username, password, role)

        if not success:
            flash("We could not create that account. Please check your information and try again.", "error")
            return redirect(url_for("auth.signup"))

        flash("Registration successful!", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get("username_or_email")
        password = request.form.get("password")

        with engine.connect() as conn:
            user = db.verify_user(conn, username_or_email, password)
            if user:
                session["user_id"] = user.user_id
                session["name"] = user.name
                session["username"] = user.username
                session["role"] = get_user_role(conn, user.user_id)
                flash("Login successful!", "success")
                return redirect(url_for("index"))

        flash("Invalid credentials. Please try again.", "error")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))
