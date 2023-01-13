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
from models import db, User, People, Planets, Fav_people, Fav_planets
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

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    if (all_people):
        people_serialize = list(map(lambda x: x.serialize(), all_people))

        return jsonify({"Hello, this is all the people": people_serialize}), 200
    else:
        return "you need to add some people, the people table is empty", 404


@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planets.query.all()
    if (all_planets):
        planets_serialize = list(map(lambda x: x.serialize(), all_planets))

        return jsonify({"Hello, this are all the planets": planets_serialize}), 200
    else:
        return "you need to add some planets, the planets table is empty", 404


# para mostrar todos los usuarios, o crear/borra uno nuevo enviándolo en el body con los datos especificados en la ruta
@app.route('/users', methods=['GET', 'POST', 'DELETE'])
def modified_user():
    body = request.get_json()
    if body is None:
        return "The request body is null", 400
    if request.method == "POST":
        if 'email' or 'username' or 'password' not in body:
            return 'You need to specify the email, password and username in a body json', 400
        else:
            email = body['email']
            password = body['password']
            username = body['username']
            new_user = User(email=email, password=password,
                            username=username, is_active=True)

            db.session.add(new_user)
            db.session.commit()
            return jsonify({
                "A new user was added!": username,
                "email": email,
                "password": password,
            }), 200
    if request.method == "DELETE":
        if 'id' not in body:
            return 'You need to specify the id in a body json ej. {"id": 1}', 400
        else:
            user_id = body['id']
            # filtra personaje a eliminar y lo retorna como objeto
            user_to_delete = User.query.filter_by(id=user_id).first()
            user_name = User.query.get(user_id).__repr__()

            db.session.delete(user_to_delete)
            db.session.commit()
            return jsonify({"deleted user": user_name}), 200

    else:
        all_users = User.query.all()
        if (all_users):
            users_serialize = list(map(lambda x: x.serialize(), all_users))
            return jsonify({"Hello this are all the users": users_serialize}), 200
        else:
            return "the user table is empty, you have to add some users", 404


@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id):
    # first para que no lo de como clase sino el objeto solo // filterby id porque es la pk de la clase people
    one_people = People.query.filter_by(id=people_id).first()
    if (one_people):
        return jsonify({
            "Hello, this is the character you are looking for ;)": one_people.serialize(),
            "id": people_id
        })
    else:
        return jsonify({"sorry :(": "This people id doesn't exist",
                        "id": people_id})


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    one_planet = Planets.query.filter_by(id=planet_id).first()
    if (one_planet):
        return jsonify({
            "Hello, this is the planet you are looking for": one_planet.serialize(),
            "id": planet_id
        })
    else:
        return jsonify({
            "sorry :(": "This planet id doesn't exist",
            "id": planet_id,

        })


# enviar un body json con el user_id ej: {"id":1}
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.get_json()['id']
    if (user_id):
        current_user = User.query.get(user_id).__repr__()

        # list con todos los favpeople que tienen ese user id
        fav_people_by_userId = Fav_people.query.filter_by(user=user_id)
        # list mapeada para serializar cada favpeople
        fav_people = list(map(lambda x: x.serialize(), fav_people_by_userId))
        # list con los ids solos
        people_id = list(map(lambda x: x['people'], fav_people))
        people_names = list(
            map(lambda x: People.query.get(x).__repr__(), people_id))

        Fav_planets_by_userId = Fav_planets.query.filter_by(
            user=user_id)  # lista de clases con los fav planets del user
        fav_planets = list(map(lambda x: x.serialize(), Fav_planets_by_userId))
        # ['planet'] da el id que es la fk guardada en favplanets.
        planet_id = list(map(lambda x: x['planet'], fav_planets))
        # busca el planeta con el id y al encontrarla como clase saca su nombre con __repr__
        planets_names = list(
            map(lambda x: Planets.query.get(x).__repr__(), planet_id))
        if fav_people or fav_planets:
            return jsonify({
                'estos son los favoritos de ': current_user,
                'favorite people': people_names,
                'favorite planets': planets_names
            }), 200
    if user_id is None:
        # no funciona da ek msj por defecto del 400
        return jsonify({'tienes que enviar un {"id":1} id de usuario'}), 400


@app.route('/favorite/people/<int:people_id>', methods=['POST', 'DELETE'])
# enviar el id del usuario en el body al hacer el request ej: {"id":1}// revisar si se puede crear usuario desde postman
def favPeople(people_id):
    body = request.get_json()
    if body is None:
        return "The request body is null", 400
    if 'id' not in body:
        return 'You need to specify the id', 400
    if request.method == 'POST':
        user = body['id']
        current_user = User.query.get(user).__repr__()
        character = People.query.get(people_id)  # personaje con el people_id
        new_favorite = Fav_people(user=user, people=people_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({
            "message": "added to favorites",
            "people id": people_id,
            "user": current_user,
        }), 200
    else:
        user = body['id']
        deleted_people = Fav_people.query.filter_by(user=user, people=people_id).first(
        )  # filtra personaje a eliminar y lo retorna como objeto((
        del_people_name = People.query.get(people_id).__repr__()

        db.session.delete(deleted_people)
        db.session.commit()
        return jsonify({"deleted people from favorites": del_people_name})


@app.route('/favorite/planet/<int:planet_id>', methods=['POST', 'DELETE'])
def favplanet(planet_id):
    body = request.get_json()
    if body is None:
        return "The request body is null", 400
    if 'id' not in body:
        return 'You need to specify the id', 400
    if request.method == 'POST':
        user = body['id']
        current_user = User.query.get(user).__repr__()
        print(current_user)
        new_favorite = Fav_planets(user=user, planet=planet_id)
        print(new_favorite)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({
            "message": "added to favorites",
            "planet id": planet_id,
            "user": current_user,
        })
    else:
        user = body['id']
        deleted_planet = Fav_planets.query.filter_by(
            user=user, planet=planet_id).first()
        del_planet_name = Planets.query.get(planet_id).__repr__()

        db.session.delete(deleted_planet)
        db.session.commit()
        return jsonify({"deleted planet from favorites": del_planet_name})


@app.route('/modifiedPeople', methods=['PUT', 'POST', 'DELETE'])
def modified_people():
    body = request.get_json()
    if body is None:
        return "The request body is null", 400
    if request.method == "POST":
        if 'name' or 'height' not in body:
            return 'You need to specify the name, and height in a body json', 400
        else:
            name = body['name']
            height = body['height']
            gender = body['gender']
            new_people = People(name=name, height=height,
                            gender=gender)

            db.session.add(new_people)
            db.session.commit()
            return jsonify({
                "A new people was added!": name,
                "height": height,
                "gender": gender,
            }), 200
    if request.method == "DELETE":
        if 'id' not in body:
            return 'You need to specify the id in a body json ej. {"id": 1}', 400
        else:
            people_id = body['id']
            # filtra personaje a eliminar y lo retorna como objeto
            people_to_delete = People.query.filter_by(id=people_id).first()
            people_name = People.query.get(people_id).__repr__()

            db.session.delete(people_to_delete)
            db.session.commit()
            return jsonify({"deleted user": people_name}), 200
# PUT
    else:
        if 'id' not in body:
            return 'You need to specify the id in a body json ej. {"id": 1}', 400
        else:
            people_id = body['id']
            # filtra personaje y lo retorna como objeto// probar a ver si funciona
            people = People.query.get(people_id)
            people_name = people.__repr__()

            people.name = body['name']
            people.height = body['height']
            people.gender = body['gender']

            db.session.commit()
            return jsonify({
                            "people modified": people_name,
                            "name": people.name,
                            "height": people.height,
                            "gender": people.gender,
                                            }), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
