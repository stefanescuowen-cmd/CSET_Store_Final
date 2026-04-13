# This is the main file for our application where we will setup the local host and Flask application.

# Imports #
from flask import Flask, redirect, render_template, request, url_for, flash
from sqlalchemy import create_engine, text
from database import DatabaseManager

app = Flask(__name__)
app.secret_key = "school_project_key"


#database setup

conn_str = "mysql://root:cset155@localhost/store_db"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()
db = DatabaseManager(conn)


#routes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        role = request.form.get("role")
        name = request.form.get("name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        if db.user_exists(email, username):
            flash("User with that email or username already exists.", "error")
            return redirect(url_for('signup'))
        
        success = db.register_new_user(name, email, username, password, role)

        if success:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('index'))
        else:
            flash("Registration failed. Please try again.", "error")
            return redirect(url_for('signup'))

    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)