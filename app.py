from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)  # Habilita CORS en toda la API

# Configuración de la base de datos desde la variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        address TEXT NOT NULL,
        cuisine TEXT NOT NULL,
        price TEXT NOT NULL
    )
''')
conn.commit()

@app.route("/add_restaurant", methods=["POST"])
def add_restaurant():
    data = request.get_json()
    try:
        cursor.execute(
            "INSERT INTO restaurants (name, city, address, cuisine, price) VALUES (%s, %s, %s, %s, %s)",
            (data["name"], data["city"], data["address"], data["cuisine"], data["price"])
        )
        conn.commit()
        return jsonify({"message": "Restaurante agregado con éxito"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_restaurants", methods=["GET"])
def get_restaurants():
    cursor.execute("SELECT name, city, address, cuisine, price FROM restaurants")
    restaurants = cursor.fetchall()
    return jsonify([{"name": r[0], "city": r[1], "address": r[2], "cuisine": r[3], "price": r[4]} for r in restaurants])

@app.route("/search_restaurants", methods=["GET"])
def search_restaurants():
    city = request.args.get("city", "")
    cuisine = request.args.get("cuisine", "")
    price = request.args.get("price", "")

    query = "SELECT name, city, address, cuisine, price FROM restaurants WHERE 1=1"
    params = []
    
    if city:
        query += " AND city ILIKE %s"
        params.append(f"%{city}%")
    if cuisine:
        query += " AND cuisine = %s"
        params.append(cuisine)
    if price:
        query += " AND price = %s"
        params.append(price)
    
    cursor.execute(query, tuple(params))
    restaurants = cursor.fetchall()
    return jsonify([{"name": r[0], "city": r[1], "address": r[2], "cuisine": r[3], "price": r[4]} for r in restaurants])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
