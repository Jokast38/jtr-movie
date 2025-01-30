from flask import Flask, render_template, request, flash
from flask_caching import Cache
import os
import requests
from dotenv import load_dotenv
import random
import time

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Vérifier si la variable d’environnement est bien définie
POKEAPI_URL = os.getenv("POKEAPI_URL")
if not POKEAPI_URL:
    raise ValueError("❌ ERREUR: La variable d'environnement POKEAPI_URL est absente du fichier .env !")

app = Flask(__name__)

# Clé secrète pour la gestion des sessions de flash messages
app.secret_key = os.getenv("SECRET_KEY", "my_secret_key")  # Définit une clé secrète pour flash()

# Configurer Flask-Caching pour utiliser un cache en mémoire
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

# Cache pendant 5 minutes
@cache.memoize(timeout=300)  

# Fonction pour récupérer les infos d'un Pokémon par ID ou nom avec cache et gestion d'erreurs
def get_pokemon_details(pokemon_name):
    """Récupère les détails d'un Pokémon avec cache."""
    try:
        # Vérifier si le Pokémon est dans le cache
        cached_data = cache.get(pokemon_name)  # Utiliser cache.get() pour récupérer du cache
        if cached_data:
            print(f"⚡ Pokémon récupéré du cache: {pokemon_name}")
            return cached_data

        # Si le Pokémon n'est pas dans le cache, on fait une requête à l'API
        print(f"🔍 Requête API pour {pokemon_name}...")
        url = f"{POKEAPI_URL}/pokemon/{pokemon_name.lower()}"
        response = requests.get(url)

        # Vérifier la réponse de l'API
        if response.status_code == 200:
            data = response.json()
            pokemon_data = {
                "name": data["name"].capitalize(),
                "hp": data["stats"][0]["base_stat"],
                "attack": data["stats"][1]["base_stat"],
                "defense": data["stats"][2]["base_stat"],
                "types": [t["type"]["name"] for t in data["types"]],
                "sprite": data["sprites"]["front_default"]
            }
            # Stocker les données dans le cache
            cache.set(pokemon_name, pokemon_data)  # Utiliser cache.set() pour ajouter dans le cache
            return pokemon_data
        else:
            print(f"❌ Erreur lors de la récupération du Pokémon: {pokemon_name}")
            return None
    except requests.RequestException as e:
        print(f"❌ Erreur réseau lors de la récupération du Pokémon {pokemon_name}: {e}")
        return None
    except Exception as e:
        print(f"❌ Une erreur inconnue est survenue pour {pokemon_name}: {e}")
        return None

# Route pour chercher un Pokémon
@app.route("/", methods=["GET", "POST"])
def home():
    pokemon = None
    comparison = None
    type_info = None

    if request.method == "POST":
        if "pokemon_name" in request.form:
            pokemon = get_pokemon_details(request.form["pokemon_name"])
            if pokemon:
                flash(f"✅ Pokémon {pokemon['name']} récupéré avec succès !", "success")
            else:
                flash(f"❌ Pokémon non trouvé.", "error")
        elif "pokemon1" in request.form and "pokemon2" in request.form:
            p1 = get_pokemon_details(request.form["pokemon1"])
            p2 = get_pokemon_details(request.form["pokemon2"])
            if p1 and p2:
                flash(f"✅ Comparaison entre {p1['name']} et {p2['name']} !", "success")
                comparison = {
                    "pokemon1": p1,
                    "pokemon2": p2,
                    "stronger": p1["attack"] > p2["attack"]
                }
            else:
                flash(f"❌ Impossible de récupérer les deux Pokémon.", "error")
        elif "pokemon_type" in request.form:
            type_info = get_pokemon_by_type(request.form["pokemon_type"])
            if type_info:
                flash(f"✅ Pokémon de type {request.form['pokemon_type']} récupérés !", "success")
            else:
                flash(f"❌ Aucun Pokémon de type {request.form['pokemon_type']} trouvé.", "error")

    return render_template("index.html", pokemon=pokemon, comparison=comparison, type_info=type_info)

if __name__ == "__main__":
    app.run(debug=True)
