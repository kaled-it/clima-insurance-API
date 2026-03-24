from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from decouple import config
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

#### CONFIGURACION DE SQLALCHEMY ####
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

### CREAMOS UNA CLASE QUE VA A CONVERTIRSE EN UNA TABLA SQL

class Insurance(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    age = db.Column(db.Integer,nullable=False)
    price = db.Column(db.Double,nullable=True)
    
    def __init__(self,age):
        self.age = age
        
### CREAMOS UN ESQUEMA PAARA SERIALIZAR LOS DATOS
ma = Marshmallow(app)
class InsuranceSchema(ma.Schema):
    id = ma.Integer()
    age = ma.Integer()
    price = ma.Float()
    
## REGISTRAMOS LA TABLA EN LA BASE DE DATOS
db.create_all()
print('Tablas en base de datos creadas')


##### HOUSING ML ################
import joblib
import numpy as np
import sklearn

model = joblib.load('./model/model.pkl')
sc_x = joblib.load('./model/scaler_x.pkl')
sc_y = joblib.load('./model/scaler_y.pkl')

def predict_price(age):
    age_sc = sc_x.transform(np.array([[age]]))
    prediction = model.predict(age_sc)
    prediction_sc = sc_y.inverse_transform(prediction)
    price = round(float(prediction_sc[0][0]),2)
    return price



@app.route('/')
def index():
    context = {
        'title':'TRABAJO FINAL MOULO 8',
        'message':'JOSE RICARDO HP : '
    }
    return jsonify(context)

@app.route('/insurance_price',methods=['POST'])
def insurance_price():
    age = request.json['age']
    price = predict_price(age)
    context = {
        'message':'precio predicho',
        'edad': age,
        'prima seguro': price
    }
    
    return jsonify(context)

@app.route('/insurance',methods=['POST'])
def set_data():
    age = request.json['age']
    price = predict_price(age)
    
    #registramos los datos en la tabla
    new_insurance = Insurance(age)
    new_insurance.price = price
    db.session.add(new_insurance)
    db.session.commit() # insert into housing ...
    
    data_schema = InsuranceSchema()
    
    context = data_schema.dump(new_insurance)
    
    return jsonify(context)

@app.route('/insurance',methods=['GET'])
def get_data():
    data = Insurance.query.all() # select * from housing
    data_schema = InsuranceSchema(many=True)
    return jsonify(data_schema.dump(data))

@app.route('/insurance/<int:id>',methods=['GET'])
def get_data_by_id(id):
    data = Insurance.query.get(id) # select * from housing where id = id
    data_schema = InsuranceSchema()
    
    return jsonify(data_schema.dump(data)),200 if data else 404

@app.route('/insurance/<int:id>',methods=['PUT'])
def update_data(id):
    data = Insurance.query.get(id) #select * from housing where id = id
    if not data:
        context = {
            'message':'Registro no encontrado'
        }
        return jsonify(context),404
    
    age = request.json['age']
    price = predict_price(age)
    
    data.age = age
    data.price = price
    db.session.commit()
    
    data_schema = InsuranceSchema()
    
    return jsonify(data_schema.dump(data)),200

@app.route('/insurance/<int:id>',methods=['DELETE'])
def delete_data(id):
    data = Insurance.query.get(id)
    
    if not data:
        context = {
            'message':'Registro no encontrado'
        }
        return jsonify(context),404
    
    db.session.delete(data) #delete from housing
    db.session.commit()
    
    context = {
        'message':'Registro eliminado correctamente'
    }
    
    return jsonify(context),200

if __name__ == '__main__':
    app.run(debug=True)