import joblib
import numpy as np
import sklearn

model = joblib.load('./model/model.pkl')
sc_x = joblib.load('./model/scaler_x.pkl')
sc_y = joblib.load('./model/scaler_y.pkl')

rooms = int(input("Ingrese el nro de habitaciones : "))
rooms_sc = sc_x.transform(np.array([[rooms]]))

prediction_sc = model.predict(rooms_sc)
prediction = sc_y.inverse_transform(prediction_sc) * 1000
print(f'El precio de una casa con {rooms} habitaciones es de : $ {prediction[0][0]:.2f}') 