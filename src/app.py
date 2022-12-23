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
    people_serialize = list(map(lambda x: x.serialize(), all_people))

    return jsonify({"Hello, GET/people response ": people_serialize}), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planets.query.all()
    planets_serialize = list(map(lambda x: x.serialize(), all_planets))

    return jsonify({"Hello, GET/planets response ": planets_serialize}), 200


@app.route('/users', methods=['GET'])
def get_user():
    all_users = User.query.all()
    # [0].__repr__//(mostrando al personaje en la posicion 0 y a la funcion repr  para dar su identificacion
    users_serialize = list(map(lambda x: x.serialize(), all_users))

    response_body = {"Hello, GET/user response ": users_serialize}

    return jsonify(response_body), 200



@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id):
    # one_people = People.query.get(people_id)#da una  clase y eso no es serializable
    # first para que no lo de como clase
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

@app.route('/users/favorites', methods=['GET'])
def get_favorites():
    # enviar el id del usuario en el body al hacer el request {"id":1}
    user_id = request.get_json()['id']#[]para acceder las propiedades del body
    current_user = User.query.get(user_id).__repr__()
    # favorite_people = Fav_people.query.all()#trayendo todos los favoritos de todos los usuarios
    # favorite_people_ser = list(map(lambda x: x.serialize(), favorite_people))#para convertirlos en diccionarios y mostrar sus valores #print("id en la posicion 1:",favorite_people_ser[1]['user'])#accediendo al id_usuario dentro del primer favorito registrado 
    # all_user_fav_people = list(map(lambda x: x['user'], favorite_people_ser))# muestra todos los id_usuario
    fav_people_by_userid = Fav_people.query.filter_by(user=user_id)#filtra solo los favoritos que contengan el user id del current user
    user_fav_people = list(map(lambda x: x.serialize(), fav_people_by_userid))
    # peoplefav=user_fav_people[2]['people']#accede al id del people agregado como favorito ej:4
    people_id = list(map(lambda x: x['people'] , user_fav_people))#accede  a los ids de los people, tengo que elegir de tabla People esos ids y acceder al name de cada id, con un map?
    people_name = list(map(lambda x: People.query.get(x) , people_id))# acceder al name de cada id, [People 'Luke Skywalker', People 'crpo', People 'r2d2']
    #people_name = People.query.filter_by(id=peoplen) aún no funciona no lo toma 
    print(people_name)
    fav_planets_by_userid = Fav_planets.query.filter_by(user=user_id)
    user_fav_planets = list(map(lambda x: x.serialize(), fav_planets_by_userid))

    return jsonify({"current user": current_user,
                    "favorite people": user_fav_people,
                    "favorite planets": user_fav_planets,
                    # "exp":people_name sale TypeError: Object of type People is not JSON serializable
                    })


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def modify_user_favorite(people_id):
        user = request.get_json()['id']  # conseguir el user _id que se envió en el body
    # if user is None:
    #         return "The request user is null", 400
    # if 'id' not in user:
    #         return 'You need to specify the id',400
    # else:
        character = People.query.get(people_id)  # personaje asociado al people_id
        new_favorite = Fav_people(user=user, people=people_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({
            "added to favorites": character.__repr__(),
            "id": people_id
        })
        
   
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite(people_id):
    deleted = Fav_people.query.filter_by(people=people_id).first()#filtra solo los people_fav que contengan el people_id
    db.session.delete(deleted)
    db.session.commit()
    return jsonify({"deleted from favorites": deleted.serialize()})


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
