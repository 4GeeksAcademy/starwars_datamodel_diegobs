"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Species, Favorites
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpointsl


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# -------------------- Endpoints Favorites -------------------- #
@app.route("/users/<int:user_id>/favorites", methods=["GET"])
def getUserFavorites(user_id):

    user = User.query.get(user_id)
    result = [favorites.serialize() for favorites in user.favorites]

    return jsonify(result)



@app.route("/users/<int:user_id>/favorites/<string:category>/<int:item_id>", methods=["POST"])
def addFavorite(user_id, category, item_id):

    validCategories = ["people", "planets"]
    if category not in validCategories:
        return jsonify({"error": "Categoría inválida"})
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"})
    
    newFav = Favorites(category=category, item_id=item_id)

    user.favorites.append(newFav)

    db.session.add(newFav)
    db.session.commit()
    
    return jsonify({"status": "ok","message": "¡Se ha añadido el favorito correctamente!"})



@app.route("/users/<int:user_id>/favorites/<string:category>/<int:item_id>", methods=["DELETE"])
def deleteFavorite(user_id, category, item_id):

    validCategories = ["people", "planets"]
    if category not in validCategories:
        return jsonify({"error": "Categoría inválida"})
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"})

    result = Favorites.query.filter(Favorites.category == category, Favorites.item_id == item_id, Favorites.user.contains(user)).first()

    db.session.delete(result)
    db.session.commit()
    
    return jsonify({"status": "ok","message": "¡Se ha borrado el favorito correctamente!"})
# ---------------------------------------------------------- #

# -------------------- Endpoints User -------------------- #
@app.route("/users", methods=["GET", "POST"])
def getOrAddUser():

    if (request.method == "GET"):
        result = User.query.all()
        result = [user.serialize() for user in result]

        return jsonify(result)

    elif (request.method == "POST"):
        dataToPost = request.get_json()
        result = User(
            email=dataToPost["email"],
            password=dataToPost["password"]
        )
        db.session.add(result)
        db.session.commit()

        return jsonify({"estado": "ok", "message": "¡El usuario se ha creado correctamente! :D"})
# ---------------------------------------------------------- #

# -------------------- Endpoints People (se llama Characters en la db) -------------------- #
@app.route("/people", methods=["GET", "POST"])
def getAll_or_addPeople():

    if (request.method == "GET"):
        result = Characters.query.all()
        result = [characters.serialize() for characters in result]

        return jsonify(result)

    elif (request.method == "POST"):
        dataToPost = request.get_json()
        result = Characters(
            name=dataToPost["name"],
            gender=dataToPost["gender"],
            species_id=dataToPost["species_id"],
            weight=dataToPost["weight"],
            height=dataToPost["height"],
            hair_color=dataToPost["hair_color"],
            eye_color=dataToPost["eye_color"],
            birth_year=dataToPost["birth_year"],
            homeworld_id=dataToPost["homeworld_id"]
        )
        db.session.add(result)
        db.session.commit()

        return jsonify({"estado": "ok", "message": "¡Se ha añadido el personaje correctamente!"})


@app.route("/people/<int:id>", methods=["GET"])
def getSingleCharacter(id):

    result = Characters.query.filter_by(id=id).first()
    return jsonify(result.serialize())


@app.route("/people/<int:id>", methods=["DELETE"])
def DeleteCharacter(id):

    result = Characters.query.filter_by(id=id).first()

    db.session.delete(result)
    db.session.commit()

    return jsonify({"estado": "ok", "message": "¡Se ha borrado el personaje correctamente!"})
# ----------------------------------------------------------- #


# -------------------- Endpoints Planets -------------------- #
@app.route("/planets", methods=["GET", "POST"])
def getAll_or_addPlanet():

    if (request.method == "GET"):
        result = Planets.query.all()
        result = [planets.serialize() for planets in result]

        return jsonify(result)

    elif (request.method == "POST"):
        dataToPost = request.get_json()
        result = Planets(
            name=dataToPost["name"],
            climate=dataToPost["climate"],
            terrain=dataToPost["terrain"],
            population=dataToPost["population"],
        )
        db.session.add(result)
        db.session.commit()

        return jsonify({"estado": "ok", "message": "¡Se ha añadido el planeta correctamente!"})
    
@app.route("/planets/<int:id>", methods=["GET"])
def getSinglePlanet(id):

    result = Planets.query.filter_by(id=id).first()
    return jsonify(result.serialize())
# ----------------------------------------------------------- #


# -------------------- Endpoints Species -------------------- #
@app.route("/species", methods=["GET", "POST"])
def getAll_or_addSpecies():

    if (request.method == "GET"):
        result = Species.query.all()
        result = [species.serialize() for species in result]

        return jsonify(result)

    elif (request.method == "POST"):
        dataToPost = request.get_json()
        result = Species(
            name=dataToPost["name"],
            classification=dataToPost["classification"],
            designation=dataToPost["designation"],
            average_height=dataToPost["average_height"],
            skin_colors=dataToPost["skin_colors"],
            hair_colors=dataToPost["hair_colors"],
            eye_colors=dataToPost["eye_colors"],
            average_lifespan_in_years=dataToPost["average_lifespan_in_years"],
            language=dataToPost["language"],
            homeworld_id=dataToPost["homeworld_id"]
        )
        db.session.add(result)
        db.session.commit()

        return jsonify({"estado": "ok", "message": "¡Se ha añadido la especie correctamente!"})
# ----------------------------------------------------------- #

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
