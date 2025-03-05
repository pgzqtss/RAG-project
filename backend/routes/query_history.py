from flask import request, jsonify
from utils.mysql_connection import connect_to_database
from __main__ import app

@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    prompt_id = data.get('prompt_id')

    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT user_input, model_output FROM history WHERE prompt_id = %s',
            (prompt_id,)
        )
        result = cursor.fetchone()
        user_input, model_output = result
        return jsonify({'message': 'Found systematic review successfully',
                        'prompt': user_input,
                        'systematic_review': model_output}), 200
    except:
        return jsonify({'error': 'No systematic review found'}), 404
    finally:
        cursor.close()
        conn.close()