from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username
            # do not serialize the password, its a security breach
        }

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    height = db.Column(db.Integer, unique=False, nullable=True)
    gender = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return 'People %r' % self.name
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "gender": self.gender
        }
    def serialize_name(self):
        return {
            "name": self.name, #no funciona con listass, la idea es ocuparlo como el serialize...que si funciona con listas
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    climate = db.Column(db.String(120), unique=False, nullable=True)
    population = db.Column(db.Integer, unique=False, nullable=True)

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population
        }
    def serialize_name(self):
        return {
            "name": self.name,
        }
class Fav_people(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    people = db.Column(db.Integer, db.ForeignKey('people.id'))
    people_rel = db.relationship('People')
    user_rel = db.relationship('User')    

    def __repr__(self):
        return  '<Fav_people %r>' % self.id

    def serialize(self):
         return {
            "id": self.id,
            "user": self.user,
            "people": self.people,
        }

#esta accediendo a cada list de favoritos en vez de a cada usuario mostrando sus favoritos....
class Fav_planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    planet = db.Column(db.Integer, db.ForeignKey('planets.id'))
    planets_rel = db.relationship('Planets')
    user_rel = db.relationship('User')

    def __repr__(self):
        return  '<Fav_planets %r>' % self.id

    def serialize(self):
         return {
            "id": self.id,
            "user": self.user,
            "planet": self.planet,
        }

