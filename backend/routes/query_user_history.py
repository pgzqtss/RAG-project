from flask import request, jsonify
from utils.mysql_connection import connect_to_database
from __main__ import app

@app.route('/api/query_user_history', methods=['POST'])
def query_user_history():
    data = request.json
    user_id = data.get('user_id')

    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT prompt_id, user_input FROM history WHERE user_id = %s ORDER BY created_at DESC',
            (user_id,)
        )
        result = cursor.fetchall()
        return jsonify({'message': 'Found user history successfully',
                        'result': result}), 200
    except:
        return jsonify({'error': 'No user history found'}), 404
    finally:
        cursor.close()
        conn.close()