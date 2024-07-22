from flask import Flask, render_template, request, url_for, redirect
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
    movies = db.session.execute(db.select(Movie).order_by(Movie.id)).scalars()
    return render_template("index.html", movies=movies.all())


@app.route("/edit", methods=['GET', 'POST'])
def update():
    if request.method == 'GET':
        movie_id = request.args.get('id')
        movie_to_edit = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
        return render_template("edit.html", movie=movie_to_edit)
    else:
        id = request.form['id']
        movie_to_edit = Movie.query.get_or_404(id)
        new_rating = request.form['rating']
        new_review = request.form['review']
        movie_to_edit.rating = new_rating
        movie_to_edit.review = new_review
        db.session.commit()
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
