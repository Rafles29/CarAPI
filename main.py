import json
from flask import Flask, request, jsonify, Response
import sqlite3

app = Flask(__name__)
Database = 'CarData.db'

def get_token(login):
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT TOKEN FROM USERS WHERE LOGIN = '{}'".format(login))
    token = ""
    for row in cursor:
        token = row[0]
    db.close()
    return token


def get_car(id):
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM CARS WHERE ID = '{}'".format(id))
    car =[]
    for row in cursor:
        car = row
    return jsonify(car_to_json(car))


def car_to_json(car):
    return {"ID": car[0], "MANUFACTOR": car[1], "MODEL": car[2], "YEAR": car[3], "FUEL": car[4], "AC": car[5],
                    "SHORT_PRICE": car[6], "MEDIUM_PRICE": car[7], "LONG_PRICE": car[8]}

def get_cars():
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM CARS")
    cars = []
    for car in cursor:
        cars.append(car_to_json(car))
    return jsonify(cars)

def acc_match(login, password):
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM USERS WHERE LOGIN = '{}'".format(login))
    for row in cursor:
        if row[2] == password:
            return True
    db.close()
    return False


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        user = request.get_json()
        login = user['login']
        password = user['password']
        if acc_match(login, password):
            return jsonify({"token": get_token(login)})
        else:
            return 'BAD'



@app.route('/cars', methods=['GET', 'POST'])
def cars():
    if request.method == 'GET':
        return get_cars()
    elif request.method == 'Post':
        return 'PostCars!'


@app.route('/cars/<string:id>', methods=['GET', 'PUT'])
def car(id):
    if request.method == 'GET':
        return get_car(id)
    elif request.method == 'PUT':
        return 'PutCar! {}'.format(id)


@app.route('/reservations', methods=['GET', "POST"])
def reservations():
    if request.method == 'GET':
        return 'GetReservations!'
    elif request.method == 'POST':
        return 'PostReservations!'


@app.route('/reservations/<id>', methods=['GET', 'DELETE'])
def show_reservation(id):
    if request.method == 'GET':
        return 'GetReservation! {}'.format(id)
    elif request.method == 'DELETE':
        return 'DeleteReservation! {}'.format(id)
def main():
    print('This is the databases.py file')

    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM USERS WHERE LOGIN = 'admin'")
    for row in cursor:
        if row[2] == 'admin1':
            print(row)
    db.close()

if __name__ == '__main__':
    app.run()