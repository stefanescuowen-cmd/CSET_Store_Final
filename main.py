#this is the main python file - owem

# Imports #
from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)

conn_str = "mysql://root:cset155@localhost"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)