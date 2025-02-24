from flask import request, jsonify
from utils.mysql_connection import connect_to_database
from __main__ import app
import bcrypt

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('SELECT id, password_hash FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        return jsonify({'message': 'User logged in successfully'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401