from flask import Flask, render_template, request, url_for, redirect
from flask_bootstrap import Bootstrap5
import requests
import os

from db import db
from movie_model import Movie

TMDB_TOKEN = os.environ.get('TMDB_TOKEN')
TMDB_REQUEST_HEADERS = {
        "accept": "application/json",
        "Authorization": "Bearer " + TMDB_TOKEN
    }

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
Bootstrap5(app)

db.init_app(app=app)

# Create table schema in the database
with app.app_context():
    db.create_all()


# Sort movies by their rating
def update_rankings():
    with app.app_context():
        movies = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars().all()
        movies = list(reversed(movies))
        for i, movie in enumerate(movies):
            movie.ranking = i + 1
        return movies


# Home page
@app.route("/")
def home():
    return render_template("index.html", movies=update_rankings())


# request to update movie rating and review by user in database and show on home
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


# Search results of a query on tmdb
def get_movie_from_query(query):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {'query': query}
    response = requests.get(url=url, params=params, headers=TMDB_REQUEST_HEADERS)
    movies = response.json()['results']
    return movies


# Render search query results and show them on /add page
@app.route("/add", methods=['GET', 'POST'])
def add_movie():
    if request.method == "POST":
        movies = get_movie_from_query(query=request.form.get('query'))
        return render_template('select.html', movies=movies)
    else:
        return render_template('add.html')


# Search selected movie by user in tmdb and add to database
@app.route("/add_movie_to_db")
def add_movie_to_db():
    tmdb_id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {'language': request.args.get('language')}
    response = requests.get(url, params=params, headers=TMDB_REQUEST_HEADERS)
    movie = response.json()
    movie_to_add = Movie(
        title=movie['original_title'],
        year=int(movie['release_date'].split('-')[0]),
        description=movie['overview'],
        img_url='https://image.tmdb.org/t/p/w500/' + movie['poster_path']
    )
    db.session.add(movie_to_add)
    db.session.commit()

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
