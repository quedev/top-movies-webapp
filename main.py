from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
import os

from db import db
from movie_model import Movie

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
Bootstrap5(app)

db.init_app(app=app)

# Create table schema in the database
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
