from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import engine
import database as db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # your login logic
    return render_template("login.html")