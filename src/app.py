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
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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

@app.route('/user', methods=['GET'])
def get_user():
    all_users = User.query.all()
    users_serialize = list(map( lambda x : x.serialize(), all_users))#[0].__repr__//(mostrando al personaje en la posicion 0 y a la funcion repr  para dar su identificacion

    response_body = {"Hello, GET/user response ": users_serialize}

    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    people_serialize = list(map( lambda x : x.serialize(), all_people))

    return jsonify({"Hello, GET/people response ": people_serialize}), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planets.query.all()
    planets_serialize = list(map( lambda x : x.serialize(), all_planets))

    return jsonify({"Hello, GET/planets response ": planets_serialize}), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id):
    #one_people = People.query.get(people_id)#da una  clase y eso no es serializable
    one_people = People.query.filter_by(id=people_id).first()#first para que no lo de como clase
    if (one_people):
        return jsonify({
                      "Hello, this is the character you are looking for ;)": one_people.serialize(),
                      "id": people_id
                      })
    else: 
        return jsonify({"sorry :(": "This people id doesn't exist",
                        "id": people_id})

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
