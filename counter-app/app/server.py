from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_db, get_counter, update_counter
import logging
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_db, get_counter, update_counter

app = Flask(__name__)
CORS(app)

# Call init_db() to initialize the database and create the table if needed
init_db()

@app.route('/counter', methods=['GET'])
def get_counter_value():
    return jsonify({"value": get_counter()})

@app.route('/counter', methods=['POST'])
def update_counter_value():
    data = request.json
    delta = data.get('delta', 0)
    update_counter(delta)
    return jsonify({"value": get_counter()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)

DB_NAME = "counter.db"
print(f"Database path: {os.path.abspath(DB_NAME)}")

logging.basicConfig(level=logging.DEBUG)

