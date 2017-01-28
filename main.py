import json
from flask import Flask, request, jsonify, make_response
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
    db.close()
    return jsonify(car_to_json(car))


def get_reservation(id):
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM RESERVATIONS WHERE ID = '{}'".format(id))
    reservation =[]
    for row in cursor:
        reservation = row
    db.close()
    return jsonify(reservation_to_json(reservation))


def get_client(id):
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM CLIENTS WHERE ID = '{}'".format(id))
    client = []

    for row in cursor:
        client = row
    db.close()
    return jsonify(client_to_json(client))


def change_quantity(id, nmb):
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT QUANTITY FROM CARS WHERE ID = '{}'".format(id))
    quantity = 0
    for row in cursor:
        quantity = row[0]
    db.execute("UPDATE CARS SET QUANTITY = {} WHERE ID = '{}'".format(quantity+nmb, id))
    db.commit()
    db.close()
    return get_car(id)


def car_to_json(car):
    return {"ID": car[0], "MANUFACTOR": car[1], "MODEL": car[2], "YEAR": car[3], "FUEL": car[4], "TRANSMISSION": car[5],
            "AC": car[6], "SHORT_PRICE": car[7], "MEDIUM_PRICE": car[8], "LONG_PRICE": car[9], "QUANTITY": car[10]}


def reservation_to_json(reservation):
    return {"ID": reservation[0], "DATE": reservation[1], "CAR_ID": reservation[2], "CLIENT_ID": reservation[3]}


def client_to_json(client):
    return {"ID": client[0], "FIRST_NAME": client[1], "LAST_NAME": client[2], "EMAIL": client[3], "PHONE": client[4], "CITY": client[5]}


def get_cars():
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM CARS")
    cars = []
    for car in cursor:
        cars.append(car_to_json(car))
    db.close()
    return jsonify(cars)


def get_reservations():
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM RESERVATIONS")
    reservations = []
    for reservation in cursor:
        reservations.append(reservation_to_json(reservation))
    db.close()
    return jsonify(reservations)


def get_clients():
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM CLIENTS")
    clients = []
    for client in cursor:
        clients.append(client_to_json(client))
    db.close()
    return jsonify(clients)


def upload_car(manu, model, year, fuel, transmission, ac, short_price, medium_price, long_price, quantity):
    db = sqlite3.connect(Database)
    cursor = db.cursor()
    cursor.execute("INSERT INTO CARS (MANUFACTOR, MODEl, YEAR, FUEL, TRANSMISSION, AC, SHORT_PRICE, MEDIUM_PRICE, LONG_PRICE, QUANTITY) \
VALUES('{}','{}',{},'{}','{}','{}',{},{},{},{})".format(manu, model, year, fuel, transmission, ac, short_price, medium_price, long_price, quantity))
    db.commit()
    db.close()
    return get_car(cursor.lastrowid)


def make_reservation(date, car_id, client_id):
    db = sqlite3.connect(Database)
    cursor = db.cursor()
    cursor.execute('''INSERT INTO RESERVATIONS(DATE, CAR_ID, CLIENT_ID)
    VALUES ('{}', {}, {})'''.format(date, car_id, client_id))
    db.commit()
    db.close()
    return get_reservation(cursor.lastrowid)


def add_client(first_name, last_name, email, phone, city):
    db = sqlite3.connect(Database)
    cursor = db.cursor()
    cursor.execute('''INSERT INTO CLIENTS(FIRST_NAME, LAST_NAME, EMAIL, PHONE, CITY)
    VALUES ('{}', '{}', '{}', '{}', '{}')'''.format(first_name, last_name, email, phone, city))
    db.commit()
    db.close()
    return get_client(cursor.lastrowid)


def delete_car(id):
    db = sqlite3.connect(Database)
    car = get_car(id)
    db.execute("DELETE FROM CARS WHERE ID = {}".format(id))
    db.commit()
    db.close()
    return car


def delete_reservation(id):
    db = sqlite3.connect(Database)
    reservation = get_reservation(id)
    db.execute("DELETE FROM RESERVATIONS WHERE ID = {}".format(id))
    db.commit()
    db.close()
    return reservation


def acc_match(login, password):
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM USERS WHERE LOGIN = '{}'".format(login))
    for row in cursor:
        if row[2] == password:
            return True
    db.close()
    return False


def token_match(token):
    db = sqlite3.connect(Database)
    cursor = db.execute("SELECT * FROM USERS WHERE TOKEN = '{}'".format(token))
    for row in cursor:
            return True
    db.close()
    return False


@app.route('/')
def hello_world():
    return 'hi'


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        user = request.get_json()
        params = ('login', 'password')
        for param in params:
            if param not in request.json:
                return make_response(jsonify({"error": "bad {}".format(param)}), 401)
        login = user['login']
        password = user['password']
        if acc_match(login, password):
            return jsonify({"token": get_token(login)})
        else:
            return make_response(jsonify({"error": "Invalid login or password"}), 400)


@app.route('/cars', methods=['GET', 'POST'])
def cars():
    if request.method == 'GET':
        return get_cars()
    elif request.method == 'POST':
        if 'token' in request.headers:
            req = request.json
            token = request.headers['token']
            if(token_match(token)):
                params = ('manufactor', 'model', 'year', 'fuel', 'transmission', 'ac', 'short_price', 'medium_price', 'long_price', 'quantity')
                for param in params:
                    if param not in req:
                        return make_response(jsonify({"error": "bad {}".format(param)}), 401)
                return upload_car(req[params[0]], req[params[1]], req[params[2]], req[params[3]], req[params[4]], req[params[5]], req[params[6]], req[params[7]], req[params[8]], req[params[9]])
            else:
                return make_response(jsonify({"error": "Invalid token"}), 401)
        else:
            return make_response(jsonify({"error": "token not found"}), 401)


@app.route('/cars/<string:id>', methods=['GET', 'PUT', 'DELETE'])
def car(id):
    if request.method == 'GET':
        return get_car(id)
    elif request.method == 'PUT':
        if 'token' in request.headers:
            req = request.json
            token = request.headers['token']
            if (token_match(token)):
                param = 'nmb'
                if param not in req:
                    return make_response(jsonify({"error": "bad {}".format(param)}), 401)
                return change_quantity(id, req[param])
            else:
                return make_response(jsonify({"error": "Invalid token"}), 401)
        else:
            return make_response(jsonify({"error": "token not found"}), 401)
    elif request.method == 'DELETE':
        if 'token' in request.headers:
            token = request.headers['token']
            if (token_match(token)):
                return delete_car(id)
            else:
                return make_response(jsonify({"error": "Invalid token"}), 401)
        else:
            return make_response(jsonify({"error": "token not found"}), 401)


@app.route('/reservations', methods=['GET', "POST"])
def reservations():
    if request.method == 'GET':
        if 'token' in request.headers:
            token = request.headers['token']
            if(token_match(token)):
                return get_reservations()
            else:
                return make_response(jsonify({"error": "Invalid token"}), 401)
        else:
            return make_response(jsonify({"error": "token not found"}), 401)
    elif request.method == 'POST':
        req = request.json
        params = ('date', 'car_id', 'client_id')
        for param in params:
            if param not in req:
                return make_response(jsonify({"error": "bad {}".format(param)}), 401)
        return make_reservation(req[params[0]], req[params[1]], req[params[2]])


@app.route('/reservations/<id>', methods=['GET', 'DELETE'])
def show_reservation(id):
    if request.method == 'GET':
        if 'token' in request.headers:
            token = request.headers['token']
            if(token_match(token)):
                return get_reservation(id)
            else:
                return make_response(jsonify({"error": "Invalid token"}), 401)
        else:
            return make_response(jsonify({"error": "token not found"}), 401)
    elif request.method == 'DELETE':
        if 'token' in request.headers:
            token = request.headers['token']
            if (token_match(token)):
                return delete_reservation(id)
            else:
                return make_response(jsonify({"error": "Invalid token"}), 401)
        else:
            return make_response(jsonify({"error": "token not found"}), 401)


@app.route('/clients', methods=['GET', "POST"])
def clients():
    if request.method == 'GET':
        if 'token' in request.headers:
            token = request.headers['token']
            if(token_match(token)):
                return get_clients()
            else:
                return make_response(jsonify({"error": "Invalid token"}), 401)
        else:
            return make_response(jsonify({"error": "token not found"}), 401)
    elif request.method == 'POST':
        req = request.json
        params = ('first_name', 'last_name', 'email', 'phone', 'city')
        for param in params:
            if param not in req:
                return make_response(jsonify({"error": "bad {}".format(param)}), 401)
        return add_client(req[params[0]], req[params[1]], req[params[2]], req[params[3]], req[params[4]])

@app.route('/clients/<id>', methods=['GET'])
def client(id):
    if request.method == 'GET':
        if 'token' in request.headers:
            token = request.headers['token']
            if(token_match(token)):
                return get_client(id)
            else:
                return make_response(jsonify({"error": "Invalid token"}), 401)
        else:
            return make_response(jsonify({"error": "token not found"}), 401)



def main():
    print('This is main')


if __name__ == '__main__':
    #main()
    app.run()