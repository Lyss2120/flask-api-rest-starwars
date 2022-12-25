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


@app.route('/users', methods=['GET'])
def get_user():
    all_users = User.query.all()
    if (all_users):
        users_serialize = list(map(lambda x: x.serialize(), all_users))
        return jsonify({"Hello this are all the users": users_serialize}), 200
    else:
        return "the user table is empty, you have to add some users", 404


@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id):
    # one_people = People.query.get(people_id)# no es serializable
    # first para que no lo de como list
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



@app.route('/users/favorites', methods=['GET'])
def get_favorites():
    # enviar el id del usuario en el body al hacer el request {"id":1}
    user_id = request.get_json()['id']
    if (user_id):
         current_user = User.query.get(user_id).__repr__()
        
         fav_people_by_userid = Fav_people.query.filter_by(user=user_id)#filtra solo los favoritos que contengan el user id del current user
         user_fav_people = list(map(lambda x: x.serialize(), fav_people_by_userid))
         people_id = list(map(lambda x: x['people'] , user_fav_people))#accede  a los ids de los people, tengo que elegir de tabla People esos ids y acceder al name de cada id, con un map?
         people_name = list(map(lambda x: People.query.get(x) , people_id))# acceder al name de cada id, [People 'Luke Skywalker', People 'crpo', People 'r2d2']
         people_name_repr= list(map(lambda x: x.__repr__(), people_name))
        
         fav_planets_by_userid = Fav_planets.query.filter_by(user=user_id)
         user_fav_planets = list(map(lambda x: x.serialize(), fav_planets_by_userid))
         planets_id = list(map(lambda x: x['planet'] , user_fav_planets))#accede  a los ids de los planets, tengo que elegir de tabla planets esos ids y acceder al name de cada id, con un map?
         planets_name = list(map(lambda x: Planets.query.get(x) , planets_id))# acceder al name de cada id, [planets 'Luke Skywalker', planets 'crpo', planets 'r2d2']
         planets_name_repr= list(map(lambda x: x.__repr__(), planets_name))
         if (people_name):
            return jsonify({"this are the favorites from the user": current_user,
                         "favorite people": people_name_repr,
                         "favorite planets": planets_name_repr,
                         # "exp":people_name sale TypeError: Object of type People is not JSON serializable
                         })
         else: return jsonify({
                            "you added to favorites this people id": people_id
         })
    else:
        return jsonify({ "you have to send de user id in a json type body": "ej: {'id':1}" })


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def modify_user_favorite(people_id):
    body = request.get_json() 
    if body is None:
            return "The request body is null", 400
    if 'id' not in body:
            return 'You need to specify the id', 400
    else:
        user = body['id']
        current_user = User.query.get(user).__repr__()
        character = People.query.get(people_id)  # personaje con el people_id
        new_favorite = Fav_people(user=user, id=people_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({
                    "message": "added to favorites",
                    "planet id": people_id,
                    "user": current_user,
                         }), 200
   
    # if not(user): #no funcionan los condicinales cuando no envio body o el body viene vacio
    #     return "<h1 style='background-color:gray' >Oh no! you have to send the user id in body, like this {'id': 1}</h1>", 400
    # if 'id' not in user:
    #          return 'You need to specify the id',400

        

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favplanet(planet_id):
    body = request.get_json() 
    if body is None:
        return "The request body is null", 400
    if 'id' not in body:
        return 'You need to specify the id', 400
    else:
        user = body['id']
        current_user = User.query.get(user).__repr__()
        new_favorite = Fav_planets(user=user, id=planet_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({
                    "message": "added to favorites",
                    "planet id": planet_id,
                    "user": current_user,
                    })


# @app.route('/favorite/people/<int:people_id>', methods=['DELETE'])# intentando borrar fav del current user
# def delete_user_favorite(people_id):
#         user = request.get_json()['id']
#         current_user = User.query.get(user).__repr__()
#         character = People.query.get(people_id)  # personaje con el people_id

#         current_user_favs = Fav_people.query.filter_by(user=user) #favs del user
#         user_favs_ser = list( map(lambda x: x.serialize() , current_user_favs)) #serializados, 
#         to_delete = Fav_people.query.get(people_id)  # personaje con el people_id. var con user favorites y borrar de ahi ?
#         print(user_favs_ser)
#         db.session.delete(to_delete)
#         db.session.commit()
#         return jsonify({
#                          "user": current_user,
#                          "deleted from favorites": character.__repr__(),
#                          })


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):

    deleted_people = Fav_people.query.filter_by(people=people_id).first()#filtra personaje a eliminar y lo retorna sin array
    db.session.delete(deleted_people)
    db.session.commit()
    return jsonify({"deleted people from favorites": deleted_people.serialize()})


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    deleted_planet = Fav_planets.query.filter_by(planet=planet_id).first()#filtra personaje a eliminar y lo retorna sin array
    db.session.delete(deleted_planet)
    db.session.commit()
    return jsonify({"deleted planet from favorites": deleted_planet.serialize()})





# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
