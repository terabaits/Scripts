from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('counter.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS counter (id INTEGER PRIMARY KEY, count INTEGER)''')
    cursor.execute('''INSERT INTO counter (id, count) SELECT 1, 0 WHERE NOT EXISTS (SELECT 1 FROM counter WHERE id = 1)''')
    conn.commit()
    conn.close()

# Get the current counter value from the database
def get_counter():
    conn = sqlite3.connect('counter.db')
    cursor = conn.cursor()
    cursor.execute('SELECT count FROM counter WHERE id = 1')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# Update the counter value in the database
def update_counter(new_count):
    conn = sqlite3.connect('counter.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE counter SET count = ? WHERE id = 1', (new_count,))
    conn.commit()
    conn.close()

@app.route('/counter', methods=['GET'])
def get_counter_route():
    count = get_counter()
    return jsonify({'count': count})

@app.route('/counter/increase', methods=['POST'])
def increase_counter():
    count = get_counter() + 1
    update_counter(count)
    socketio.emit('update', {'count': count}, broadcast=True)
    return jsonify({'count': count})

@app.route('/counter/decrease', methods=['POST'])
def decrease_counter():
    count = get_counter() - 1
    update_counter(count)
    socketio.emit('update', {'count': count}, broadcast=True)
    return jsonify({'count': count})

@socketio.on('connect')
def handle_connect():
    count = get_counter()
    emit('update', {'count': count})

if __name__ == "__main__":
    init_db()
    socketio.run(app, host='0.0.0.0', port=3001)
