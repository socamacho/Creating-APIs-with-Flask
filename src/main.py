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

#JWT-SECURITY
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

app = Flask(__name__)#Creo nueva instancia del servidor Flask
app.url_map.strict_slashes = False #DUDA: Que significa?
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING') #Para conectarme a la DB, arcivo env.example crea el enlace.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Cuando yo hago modificaciones en models.py, va a crear la migracion de la DB. DUDA: Conectada a pipenv run migrate?
MIGRATE = Migrate(app, db) #Se lleva a cabo la migracion.
db.init_app(app) #Se inicializa la app.
CORS(app) #DUDA: CROSS ORIGIN RESOURCE SHARING. No se que putas??
setup_admin(app)#DUDA: Maneja la funcionalidad de la app por medio de flask.


#Set up the FLASK-JWT-Extended extension  
#app.config["JWT_SECRET_KEY"] = "super-secret"
#jwt = JWTManager(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException) #Ayuda a que los errores se vean mas bonitos en forma de JSON (linea 25-27)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')   #Este endpoint (lineas 29-31) ayudan a que cuanto no se agrega un dominio al URL, aparezca Rigo bby. Codigo linea 30, CREA una ruta adicionalmente, 
              #especifica que el endpoint va a estar disponible de ahora en adelante. Aqui se esta aplicando metodo GET.
def sitemap():
    return generate_sitemap(app)
#----------------------------------EVERYTHING related to the USER------------------------------------------------------------------------------------------------------
@app.route('/user', methods=['GET']) 
def Get_Users_Info(): #Cuando el cliente realizada el request, esta llamando este metodo.
    users_query= User.query.all() #Obtiene toda la info de users
    all_users_request = list(map(lambda user: user.serialize(), users_query)) #Mapea los resultados y su lista de gente dentro de la variable users_query.
    return jsonify(all_users_request), 200

#-----------METODO GET------------------------------------------------------->
@app.route('/user/<int:id>', methods=['GET'])
def Deploy_User_Info(id): #Coloco de parametro el id porque es la forma de identificar un UNICO user.
    user = User.query.filter_by(id = id).first()#Otra forma de hacerlo seria User.query.get(id)//El first es para evitar obtener info DUPLICADA.NO es buena practica ya que puede buscarse info generalizada.
    if user is None: 
        raise APIException("Message: No se encontro el user",status_code=404)
    request = user.serialize() 
    return jsonify(request), 200


#-----------METODO POST---------------------------------------------------->

@app.route('/user', methods= ['POST'])
def Create_Users():
    is_active = request.json.get("is_active", True) #Solo este CON TRUE por ser boolean. 
    username = request.json.get("username", None)
    email = request.json.get("email", None)
    password = request.json.get("password",None)#El None ES por si no tengo un dado, sale NONE.

    #hashed_password = generate_password_hash(data["password"], method='sha256')
    #user1 = User(is_active=data['is_active'],username=data['username'],email=data['email'],password=data['password'])
    user1 = User(is_active = is_active, username= username, email=email, password=password)
    db.session.add(user1) #Agrega el user
    db.session.commit()#Sube User1 a la DB.
    return jsonify("Message: Se adiciono un usuario!",200)


#-----------METODO DELETE---------------------------------------------------->

@app.route('/user/<id>', methods=["DELETE"])
#@jwt_required()
def Delete_Users(id):
    #current_user = get_jwt_identity() #Este get_jwt_identity() fue importado.
    user1= User.query.filter_by(id=id).first()
    if user1 is None:
        raise APIException("Usuario no existe!",status_code=404)
    db.session.delete(user1)
    db.session.commit()
    return jsonify({"Proceso realizado con exito por el usuario:" : user1.serialize()}),200








# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


"""user1 = Person.query.get(person_id)
if user1 is None:
   raise APIException('User not found', status_code=404)
db.session.delete(user1)
db.session.commit()"""