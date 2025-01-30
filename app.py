from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Récupérer la clé API depuis le fichier .env
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Fonction pour récupérer les infos d'un film par ID
def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "language": "fr-FR"}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "title": data.get("title"),
            "release_date": data.get("release_date"),
            "genres": [genre["name"] for genre in data.get("genres", [])],
            "popularity": data.get("popularity"),
            "vote_average": data.get("vote_average"),
            "overview": data.get("overview"),
            "poster_path": f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}"
        }
    else:
        return None

def get_latest_movies():
    url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=fr-FR&page=1'
    response = requests.get(url)
    return response.json().get('results', [])

# Route principale avec formulaire de recherche    
@app.route("/", methods=["GET", "POST"])
def home():
    movie = None
    latest_movies = get_latest_movies()
    if request.method == "POST":
        movie_id = request.form["movie_id"]
        movie = get_movie_details(movie_id)
    
    return render_template("index.html", latest_movies=latest_movies, movie=movie)

if __name__ == "__main__":
    app.run(debug=True)
