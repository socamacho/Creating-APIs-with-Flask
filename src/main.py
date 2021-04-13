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
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING') #Para conectarme a la DB, arcivo env.example crea el enlace.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Cuando yo hago modificaciones en models.py, va a crear la migracion de la DB. 
MIGRATE = Migrate(app, db) #Se lleva a cabo la migracion.
db.init_app(app) #Se inicializa la app.
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException) #Ayuda a que los errores se ven mas bonitos (linea 24-26)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')   #Este endpoint (lineas 29-31) ayudan a que cuanto no se agrega un domino al URL, aparezac Rigo bby.
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    people_query = User.query.all()
    all_people = list(map(lambda x: x.serialize(), people_query))

    return jsonify(all_people), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


user1 = Person.query.get(person_id)
if user1 is None:
   raise APIException('User not found', status_code=404)
db.session.delete(user1)
db.session.commit()