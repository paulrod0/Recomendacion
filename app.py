from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Configuración de la conexión a PostgreSQL desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

def connect_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Crear la tabla si no existe
conn = connect_db()
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id SERIAL PRIMARY KEY,
        name TEXT,
        city TEXT,
        address TEXT,
        cuisine TEXT,
        price TEXT
    )''')
conn.commit()
conn.close()

@app.route("/add_restaurant", methods=["POST"])
def add_restaurant():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO restaurants (name, city, address, cuisine, price) VALUES (%s, %s, %s, %s, %s)",
                   (data['name'], data['city'], data['address'], data['cuisine'], data['price']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Restaurante agregado con éxito"}), 201

@app.route("/get_restaurants", methods=["GET"])
def get_restaurants():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM restaurants")
    restaurants = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "city": r[2], "address": r[3], "cuisine": r[4], "price": r[5]} for r in restaurants])

@app.route("/search_restaurants", methods=["GET"])
def search_restaurants():
    city = request.args.get("city", "")
    cuisine = request.args.get("cuisine", "")
    price = request.args.get("price", "")
    query = "SELECT * FROM restaurants WHERE 1=1"
    params = []

    if city:
        query += " AND city ILIKE %s"
        params.append(f"%{city}%")
    if cuisine:
        query += " AND cuisine ILIKE %s"
        params.append(f"%{cuisine}%")
    if price:
        query += " AND price = %s"
        params.append(price)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    restaurants = cursor.fetchall()
    conn.close()
    
    return jsonify([{"id": r[0], "name": r[1], "city": r[2], "address": r[3], "cuisine": r[4], "price": r[5]} for r in restaurants])

if __name__ == "__main__":
    app.run(debug=True)
