from flask import Flask, render_template, request
import requests
import random
import os
from dotenv import load_dotenv


# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Vérifier si la variable d’environnement est bien définie
POKEAPI_URL = os.getenv("POKEAPI_URL")
if not POKEAPI_URL:
    raise ValueError("❌ ERREUR: La variable d'environnement POKEAPI_URL est absente du fichier .env !")


app = Flask(__name__)

# Fonction pour récupérer les infos d'un Pokémon par ID ou nom
def get_pokemon_details(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "name": data["name"].capitalize(),
            "hp": data["stats"][0]["base_stat"],
            "attack": data["stats"][1]["base_stat"],
            "defense": data["stats"][2]["base_stat"],
            "types": [t["type"]["name"] for t in data["types"]],
            "sprite": data["sprites"]["front_default"]
        }
    else:
        return None

# Fonction pour récupérer les Pokémon d'un type donné
def get_pokemon_by_type(type_name):
    url = f"https://pokeapi.co/api/v2/type/{type_name.lower()}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        pokemon_list = data["pokemon"]
        total_hp = 0
        count = len(pokemon_list)

        for p in pokemon_list:
            pokemon_details = get_pokemon_details(p["pokemon"]["name"])
            if pokemon_details:
                total_hp += pokemon_details["hp"]

        avg_hp = total_hp / count if count > 0 else 0
        return {"count": count, "avg_hp": avg_hp}
    else:
        return None
    
# Fonction pour simuler un combat entre 2 Pokémon
def simulate_battle(pokemon1, pokemon2):
    p1_hp = pokemon1["hp"]
    p2_hp = pokemon2["hp"]

    for _ in range(5):  # 5 tours de combat
        p2_hp -= max(1, pokemon1["attack"] - random.randint(0, 5))
        p1_hp -= max(1, pokemon2["attack"] - random.randint(0, 5))

        if p1_hp <= 0 or p2_hp <= 0:
            break

    winner = pokemon1["name"] if p1_hp > p2_hp else pokemon2["name"]
    return {"winner": winner, "p1_hp": p1_hp, "p2_hp": p2_hp}    

# Route pour chercher un Pokémon
@app.route("/", methods=["GET", "POST"])
def home():
    pokemon = None
    comparison = None
    type_info = None

    if request.method == "POST":
        if "pokemon_name" in request.form:
            pokemon = get_pokemon_details(request.form["pokemon_name"])
        elif "pokemon1" in request.form and "pokemon2" in request.form:
            p1 = get_pokemon_details(request.form["pokemon1"])
            p2 = get_pokemon_details(request.form["pokemon2"])
            if p1 and p2:
                comparison = {
                    "pokemon1": p1,
                    "pokemon2": p2,
                    "stronger": p1["attack"] > p2["attack"]
                }
        elif "pokemon_type" in request.form:
            type_info = get_pokemon_by_type(request.form["pokemon_type"])

    return render_template("index.html", pokemon=pokemon, comparison=comparison, type_info=type_info)

@app.route("/battle", methods=["GET", "POST"])
def battle():
    battle_result = None
    if request.method == "POST":
        p1 = get_pokemon_details(request.form["pokemon1"])
        p2 = get_pokemon_details(request.form["pokemon2"])

        if p1 and p2:
            battle_result = simulate_battle(p1, p2)

    return render_template("battle.html", battle_result=battle_result)

if __name__ == "__main__":
    app.run(debug=True)
