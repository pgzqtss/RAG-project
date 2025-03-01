from flask import request, jsonify
from utils.mysql_connection import connect_to_database
from __main__ import app

@app.route('/api/query_user', methods=['POST'])
def query_user():
    data = request.json
    username = data.get('username')
    print(f'Username: {username}')

    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT id FROM users WHERE username = %s',
            (username,)
        )
        result = cursor.fetchone()
        return jsonify({'message': 'Found user successfully',
                        'user_id': result}), 200
    except:
        return jsonify({'error': 'No user found'}), 404
    finally:
        cursor.close()
        conn.close()