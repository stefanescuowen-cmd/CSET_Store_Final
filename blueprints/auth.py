from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from extensions import engine
import database as db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Your login logic here
    return render_template("login.html")