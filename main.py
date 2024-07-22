from flask import Flask, render_template, request, url_for, redirect
from flask_bootstrap import Bootstrap5
import requests
import os

from db import db
from movie_model import Movie

TMDB_TOKEN = os.environ.get('TMDB_TOKEN')

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
        movie_id = request.form['id']
        movie_to_edit = Movie.query.get_or_404(movie_id)
        new_rating = request.form['rating']
        new_review = request.form['review']
        movie_to_edit.rating = new_rating
        movie_to_edit.review = new_review
        db.session.commit()
        return redirect(url_for('home'))


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get_or_404(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


def get_movie_from_query(query):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {'query': query}
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + TMDB_TOKEN
    }
    response = requests.get(url=url, params=params, headers=headers)
    response.raise_for_status()
    movies = [(movie['original_title'], movie['release_date']) for movie in response.json()['results']]
    return movies


@app.route("/add", methods=['GET', 'POST'])
def add_movie():
    if request.method == "GET":
        return render_template('add.html')
    else:
        movies = get_movie_from_query(query=request.form.get('query'))
        return render_template('select.html', movies=movies)


if __name__ == '__main__':
    app.run(debug=True)
